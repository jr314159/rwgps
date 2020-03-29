#!/usr/bin/env python3
"""A script to merge multiple KML files.

Also optionally helps reduce file size by skipping coordinates.
This is useful since Google Maps has a 5MB file size limit, and
a limit of 10 layers per map.

"""
import xml.etree.ElementTree as ET
import os
from itertools import cycle
import argparse


NS = {"kml": "http://www.opengis.net/kml/2.2"}
ET.register_namespace("", NS["kml"])


def extract_placemark_from_file(f):
    return ET.parse(f).find(".//kml:Placemark", NS)


def build_tree_from_files(files):
    tree = None
    doc = None

    for f in files:
        print("Loading {}".format(f))
        if tree is None:
            tree = ET.parse(f)
            doc = tree.find(".//kml:Document", NS)
            continue
        else:
            placemark = extract_placemark_from_file(f)
            doc.append(placemark)

    return tree


def compress_lines(tree, rate=5):
    for coords in tree.findall(".//kml:coordinates", NS):
        coords.text = "\n".join(coord for coord, i in zip(
            (coord for coord in coords.text.split()), cycle(range(rate))
        ) if i == 0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge and compress KML files.")
    parser.add_argument("output", help="Output file")
    parser.add_argument("input", nargs="+", help="Input files")
    parser.add_argument("--rate", help="Compression rate", type=int, default=1)
    args = parser.parse_args()

    print("Building tree...")
    tree = build_tree_from_files([os.path.abspath(f) for f in args.input])

    print("Compressing tree...")
    compress_lines(tree, rate=args.rate)

    print("Writing to {}".format(args.output))
    tree.write(args.output, xml_declaration=True)


