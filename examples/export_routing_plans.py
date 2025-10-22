"""
Example: Export All Routing Plans to JSON Files

This script retrieves all routing profiles and their associated plans,
then exports each plan to a separate JSON file named:
    profileName_planName.json

Usage:
    python export_routing_plans.py [--output-dir OUTPUT_DIR]

Arguments:
    --output-dir: Directory to save exported plans (default: routing_plans_export)
"""

import argparse
import json
import logging
from pathlib import Path

from config import Config
from ofsc import OFSC

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def sanitize_filename(name: str) -> str:
    """
    Sanitize a string to be used as a filename.

    Removes or replaces characters that are not safe for filenames.
    """
    # Replace spaces with underscores
    name = name.replace(" ", "_")
    # Remove or replace unsafe characters
    unsafe_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for char in unsafe_chars:
        name = name.replace(char, "_")
    return name


def export_all_routing_plans(output_dir: str = "routing_plans_export"):
    """
    Export all routing plans from all profiles to JSON files.

    Args:
        output_dir: Directory where JSON files will be saved
    """
    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    logger.info(f"Output directory: {output_path.absolute()}")

    # Initialize OFSC connection
    logger.info("Connecting to OFSC...")
    instance = OFSC(
        clientID=Config.OFSC_CLIENT_ID,
        secret=Config.OFSC_CLIENT_SECRET,
        companyName=Config.OFSC_COMPANY,
    )
    logger.info(f"Connected to {Config.OFSC_COMPANY}")

    # Get all routing profiles
    logger.info("Retrieving routing profiles...")
    profiles = instance.metadata.get_routing_profiles()

    if not profiles.items:
        logger.warning("No routing profiles found")
        return

    logger.info(f"Found {len(profiles.items)} routing profile(s)")

    # Track statistics
    total_plans_exported = 0

    # Iterate through each profile
    for profile in profiles.items:
        profile_label = profile.profileLabel
        logger.info(f"\nProcessing profile: {profile_label}")

        # Get all plans for this profile
        plans = instance.metadata.get_routing_profile_plans(
            profile_label=profile_label
        )

        if not plans.items:
            logger.info(f"  No plans found in profile '{profile_label}'")
            continue

        logger.info(f"  Found {len(plans.items)} plan(s) in '{profile_label}'")

        # Export each plan
        for plan in plans.items:
            plan_label = plan.planLabel
            logger.info(f"    Exporting plan: {plan_label}")

            try:
                # Export the routing plan
                plan_data = instance.metadata.export_routing_plan(
                    profile_label=profile_label,
                    plan_label=plan_label
                )

                # Create filename: profileName_planName.json
                safe_profile = sanitize_filename(profile_label)
                safe_plan = sanitize_filename(plan_label)
                filename = f"{safe_profile}_{safe_plan}.json"
                filepath = output_path / filename

                # Convert Pydantic model to dict for JSON serialization
                plan_dict = plan_data.model_dump()

                # Write to JSON file with pretty formatting
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(plan_dict, f, indent=2, ensure_ascii=False)

                logger.info(f"    ✓ Saved to: {filename}")
                total_plans_exported += 1

            except Exception as e:
                logger.error(f"    ✗ Error exporting {plan_label}: {e}")

    # Summary
    logger.info(f"\n{'='*60}")
    logger.info(f"Export complete!")
    logger.info(f"Total profiles processed: {len(profiles.items)}")
    logger.info(f"Total plans exported: {total_plans_exported}")
    logger.info(f"Files saved to: {output_path.absolute()}")
    logger.info(f"{'='*60}")


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Export all routing plans to JSON files"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="routing_plans_export",
        help="Directory to save exported plans (default: routing_plans_export)"
    )

    args = parser.parse_args()

    try:
        export_all_routing_plans(output_dir=args.output_dir)
    except Exception as e:
        logger.error(f"Script failed: {e}", exc_info=True)
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
