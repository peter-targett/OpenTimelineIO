#!/usr/bin/env python
#
# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""Tests for the OTIOZ adapter."""

import unittest
import os
import stat
import sys
import zipfile
import pathlib
import tempfile

import opentimelineio as otio
import opentimelineio.test_utils as otio_test_utils


class OTIOZTester(unittest.TestCase, otio_test_utils.OTIOAssertions):
    def test_round_trip(self):
        with tempfile.TemporaryDirectory() as temp_dir:

            # Create a timeline
            tl = otio.schema.Timeline()
            tr = otio.schema.Track()
            tl.tracks.append(tr)
            cl = otio.schema.Clip()
            tr.append(cl)

            # Add a media reference
            ref = otio.schema.ExternalReference("video.mov")
            cl.media_reference = ref
            pathlib.Path(os.path.join(temp_dir, ref.target_url)).touch()

            # Write to otioz
            otioz_path = os.path.join(temp_dir, "round_trip.otioz")
            otio.adapters.write_to_file(
                tl,
                otioz_path,
                relative_media_base_dir=temp_dir)

            # Read from otiod
            result = otio.adapters.read_from_file(otioz_path)
            self.assertIsNotNone(result)


    @unittest.skipIf(sys.platform == "win32", "no Unix permissions")
    def test_text_entry_permissions(self):
        """content.otio and version.txt are written from memory, and must
        still extract as readable files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            otioz_path = os.path.join(temp_dir, "perms.otioz")
            otio.adapters.write_to_file(otio.schema.Timeline(), otioz_path)

            with zipfile.ZipFile(otioz_path) as z:
                for name in ("content.otio", "version.txt"):
                    mode = z.getinfo(name).external_attr >> 16
                    self.assertTrue(stat.S_ISREG(mode), name)
                    self.assertTrue(mode & stat.S_IRUSR, name)

            extract_path = os.path.join(temp_dir, "extracted")
            otio.adapters.read_from_file(
                otioz_path, extract_to_directory=extract_path)
            content = os.path.join(extract_path, "content.otio")
            self.assertTrue(os.stat(content).st_mode & stat.S_IRUSR)
            with open(content) as f:
                self.assertIn("Timeline", f.read())

    @unittest.skipIf(sys.platform == "win32", "no Unix permissions")
    def test_extract_old_bundle_without_permissions(self):
        """Bundles written by older OTIO have no permissions on their text
        entries; they must still extract as readable files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            otioz_path = os.path.join(temp_dir, "old.otioz")
            content = otio.adapters.write_to_string(
                otio.schema.Timeline(), "otio_json")
            with zipfile.ZipFile(otioz_path, "w") as z:
                for name, data in (("version.txt", "1.0.0"),
                                   ("content.otio", content)):
                    info = zipfile.ZipInfo(name)
                    info.create_system = 3      # Unix, mode 0
                    info.external_attr = 0
                    z.writestr(info, data)

            extract_path = os.path.join(temp_dir, "extracted")
            otio.adapters.read_from_file(
                otioz_path, extract_to_directory=extract_path)
            for name in ("content.otio", "version.txt"):
                mode = os.stat(os.path.join(extract_path, name)).st_mode
                self.assertTrue(mode & stat.S_IRUSR, name)

if __name__ == "__main__":
    unittest.main()
