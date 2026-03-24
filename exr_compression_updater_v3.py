#!/usr/bin/env python3

import sys
import logging
from pathlib import Path
from typing import Dict, List, Optional
import xml.etree.ElementTree as ET
import OpenEXR


# Type Definitions
ShotData = Dict[str, str]
ProjectData = Dict[str, Optional[str]]


# External file paths
LOG_FILE = Path.home() / "~path-to-directory~/updater_log.txt"
DEFAULT_OUTPUT_FILE = Path.home() / "~path-to-directory~/updated_metadata.xml"


# Set up logging
def setup_logging() -> None:
    """Configure logging with proper format and file location."""
    file_handler = logging.FileHandler(LOG_FILE)
    stream_handler = logging.StreamHandler()

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[file_handler, stream_handler]
    )

    # Add a separator at the beginning of the script run
    #logging.info("\n" + "=" * 40 + "Script running" + "=" * 40)
    #logging.info("Script execution started")
    #logging.info("=" * 80)


# Read metadata from EXR file
def read_exr_metadata(file_path: str) -> Dict[str, str]:
    """Read compression, data window, and display window metadata from an EXR file."""
    try:
        if not file_path.lower().endswith(".exr"):
            logging.warning(f"Skipping non-EXR file: {file_path}")
            return {"compression": "Unknown", "data_window": "Unknown", "display_window": "Unknown"}

        exr_file = OpenEXR.InputFile(file_path)
        header = exr_file.header()

        metadata = {
            "compression": str(header.get("compression", "Unknown")),
            "data_window": str(header.get("dataWindow", "Unknown")),
            "display_window": str(header.get("displayWindow", "Unknown")),
        }

        exr_file.close()
        logging.info(f"Extracted metadata from {file_path}:")
        logging.info(f"  Compression: {metadata['compression']}")
        logging.info(f"  Data Window: {metadata['data_window']}")
        logging.info(f"  Display Window: {metadata['display_window']}")
        return metadata

    except Exception as e:
        logging.error(f"Error reading EXR file {file_path}: {e}")
        return {"compression": "Unknown", "data_window": "Unknown", "display_window": "Unknown"}


# Parse input XML
def parse_input_xml(xml_file: str) -> ProjectData:
    """Parse the input XML and extract project and shot data."""
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()

        project_data: ProjectData = {
            "project_name": root.attrib.get("project", "Unknown"),
            "group_name": "Unknown",
            "construct_name": "Unknown",
            "shots": [],
            "watch_folder": root.attrib.get("watch_folder"),
        }

        # Extract group and construct names
        selection = root.find(".//selection")
        if selection is not None:
            project_data["group_name"] = selection.attrib.get("group", "Unknown")
            project_data["construct_name"] = selection.attrib.get("construct", "Unknown")

        # Extract shots
        shots = []
        for shot_element in root.findall(".//selection/shot"):
            shot_data = {
                "slot_index": shot_element.attrib.get("slot", "Unknown"),
                "shot_layer": shot_element.attrib.get("layer", "Unknown"),
                "file_path": shot_element.findtext(".//file", "Unknown").strip(),
                "shot_name": shot_element.findtext(".//name", "Unknown").strip(),
                "metadata": [],
            }

            # Extract metadata
            metadata_elements = shot_element.findall(".//metadata/dataitem")
            for dataitem in metadata_elements:
                key = dataitem.findtext("key", "Unknown").strip()
                value = dataitem.findtext("value", "Unknown").strip()
                shot_data["metadata"].append({"key": key, "value": value})

            # Extract EXR-specific metadata
            if shot_data["file_path"] and shot_data["file_path"] != "Unknown":
                exr_metadata = read_exr_metadata(shot_data["file_path"])
                shot_data.update(exr_metadata)

            shots.append(shot_data)

        project_data["shots"] = shots

        logging.info("Extracted project data:")
        logging.info(f"  Project Name: {project_data['project_name']}")
        logging.info(f"  Group Name: {project_data['group_name']}")
        logging.info(f"  Construct Name: {project_data['construct_name']}")
        logging.info(f"  Watch Folder: {project_data['watch_folder']}")

        for i, shot in enumerate(project_data["shots"], start=1):
            logging.info(f"  Shot {i}:")
            logging.info(f"    Slot Index: {shot['slot_index']}")
            logging.info(f"    Shot Layer: {shot['shot_layer']}")
            logging.info(f"    File Path: {shot['file_path']}")
            logging.info(f"    Shot Name: {shot['shot_name']}")
            for metadata_item in shot["metadata"]:
                logging.info(f"    Metadata - {metadata_item['key']}: {metadata_item['value']}")
            logging.info(f"    Compression: {shot.get('compression', 'Unknown')}")
            logging.info(f"    Data Window: {shot.get('data_window', 'Unknown')}")
            logging.info(f"    Display Window: {shot.get('display_window', 'Unknown')}")

        return project_data

    except Exception as e:
        logging.error(f"Error parsing XML file {xml_file}: {e}")
        sys.exit(1)


# Generate new XML
def generate_new_xml(data: ProjectData, output_path: Path) -> None:
    """Generate a new XML file with updated metadata."""
    try:
        root = ET.Element("scratch", log_file=str(output_path))

        # Create <commands> structure
        commands = ET.SubElement(root, "commands")
        command = ET.SubElement(
            commands,
            "command",
            action="update",
            project=data["project_name"],
            command_id="metadata_update",
        )

        groups = ET.SubElement(command, "groups")
        group = ET.SubElement(groups, "group", name=data["group_name"])
        constructs = ET.SubElement(group, "constructs")
        construct = ET.SubElement(constructs, "construct", name=data["construct_name"])
        slots = ET.SubElement(construct, "slots")

        # Add shots
        for shot in data["shots"]:
            slot = ET.SubElement(slots, "slot", index=shot["slot_index"])
            shots = ET.SubElement(slot, "shots")
            shot_element = ET.SubElement(shots, "shot", layer=shot["shot_layer"])

            ET.SubElement(shot_element, "file").text = shot["file_path"]
            ET.SubElement(shot_element, "name").text = shot["shot_name"]

            # Add metadata
            metadata = ET.SubElement(shot_element, "metadata")
            for item in shot["metadata"]:
                dataitem = ET.SubElement(metadata, "dataitem")
                ET.SubElement(dataitem, "key").text = item["key"]
                ET.SubElement(dataitem, "value").text = item["value"]

            # Add EXR-specific metadata (already extracted in parse_input_xml)
            for key in ["compression", "data_window", "display_window"]:
                if key in shot and shot[key] != "Unknown":
                    dataitem = ET.SubElement(metadata, "dataitem")
                    ET.SubElement(dataitem, "key").text = key.replace("_", " ").title()
                    ET.SubElement(dataitem, "value").text = shot[key]

        # Write XML to file
        tree = ET.ElementTree(root)
        tree.write(output_path, encoding="utf-8", xml_declaration=True)
        logging.info(f"Generated XML saved to {output_path}")

    except Exception as e:
        logging.error(f"Error generating XML file: {e}")
        sys.exit(1)


# Main function
def main() -> None:
    setup_logging()

    if len(sys.argv) < 2:
        logging.error("Usage: python exr_compression_updater_v3.py <input_xml>")
        sys.exit(1)

    input_xml = Path(sys.argv[1])
    if not input_xml.exists():
        logging.error(f"Input XML file not found: {input_xml}")
        sys.exit(1)

    # Parse input XML
    data = parse_input_xml(str(input_xml))

    # Determine output paths
    output_paths = []
    if data["watch_folder"]:
        output_paths.append(Path(data["watch_folder"]) / "updated_metadata.xml")
    output_paths.append(DEFAULT_OUTPUT_FILE)

    # Generate XML files
    for output_path in output_paths:
        generate_new_xml(data, output_path)

    # Add a separator at the end of the script run
    logging.info("=" * 40 + "[" + "custom command completed" + "]" + "=" * 40)
    #logging.info("Script execution completed")
    #logging.info("=" * 80)


if __name__ == "__main__":
    main()
