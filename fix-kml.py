#!/usr/bin/env python3
"""A script to fix KML files exported from Ride With GPS.

Google Maps doesn't like the KML that RWGPS produces.  Mainly the issue
seems to be with trailing commas on coordinates that have no altitude recorded.
This script seems to do the trick.

"""
import argparse
import logging
import os
import xml.etree.ElementTree as ET

NS = {"kml": "http://www.opengis.net/kml/2.2"}


def fix_kml(inf, outf):
    """Fix a broken KML file.

    Corrects the <altitudeMode> from "clampedToGround" to "clampToGround"
    (https://developers.google.com/kml/documentation/kmlreference#elements-specific-to-linestring),
    and removes trailing commas where altitude is missing.

    Args:
        inf: Path to the broken file.
        outf: Path of the fixed filename to write to.

    """
    ET.register_namespace("", NS["kml"])
    tree = ET.parse(inf)
    ls = tree.find(".//kml:LineString", NS)
    ls.find("kml:altitudeMode", NS).text = "clampToGround"
    coords = ls.find("kml:coordinates", NS)
    coords.text = "\n".join((",".join(component for component in coord.split(",") if component)
        for coord in coords.text.split()
    ))
    tree.write(outf, xml_declaration=True)


def fix_dir(ind, outd):
    """Fix a directory full of broken KML files.

    Args:
        ind: Path to input directory.
        outd: Path to output directory.

    """
    for f in os.listdir(ind):
        inf = os.path.join(ind, f)
        outf = os.path.join(outd, f)
        logging.info("Fixing {} -> {}".format(inf, outf))
        fix_kml(inf, outf)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="Fix the broken KML that RWGPS exports.")
    parser.add_argument("input", help="Input directory")
    parser.add_argument("output", help="Output directory")
    args = parser.parse_args()

    logging.info("Fixing files in {}, writing to {}".format(args.input, args.output))
    fix_dir(args.input, args.output)
    logging.info("Done")