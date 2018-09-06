#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import argparse
from ios_builder import iOSBuilder
from pgyer_uploader import upload_ipa_to_pgyer, save_qrcode_image


def parse_args():
    parser = argparse.ArgumentParser(description='iOS app build script.')

    parser.add_argument('--build_method', dest="build_method", default='xcodebuild',
                        help="Specify build method, xctool or xcodebuild.")
    parser.add_argument('--workspace', dest="workspace", default=None,
                        help="Build the workspace name.xcworkspace")
    parser.add_argument("--scheme", dest="scheme", default=None,
                        help="Build the scheme specified by schemename. \
                        Required if building a workspace")
    parser.add_argument("--project", dest="project", default=None,
                        help="Build the project name.xcodeproj")
    parser.add_argument("--target", dest="target", default=None,
                        help="Build the target specified by targetname. \
                        Required if building a project")
    parser.add_argument("--sdk", dest="sdk", default='iphoneos',
                        help="Specify build SDK, iphoneos or iphonesimulator, \
                        default is iphoneos")
    parser.add_argument("--build_version_plist_path", dest="build_version_plist_path", default=None,
                        help="Specify build plist path")
    parser.add_argument("--export_options_plist_path", dest="export_options_plist_path", default=None,
                        help="Specify export options plist path")
    parser.add_argument("--configuration", dest="configuration", default='Debug',
                        help="Specify build configuration, Release or Debug, \
                        default value is Debug")
    parser.add_argument("--output_folder", dest="output_folder", required=True,
                        help="specify output_folder folder name")
    parser.add_argument("--package_type", dest="package_type", default=None,
                        help="specify package type")
    parser.add_argument("--password", dest="password", default=None,
                        help="specify current user's password to unlock keychain")
    parser.add_argument("--fabric_key", dest="fabric_key", default=None,
                        help="specify fabric key to upload dSYM")
    parser.add_argument("--env", dest="env", default=None, choices=['online', 'pre', 'test'],
                        help="server environment")

    args = parser.parse_args()
    print("args: {}".format(args))
    return args


def main():
    args = parse_args()

    ios_builder = iOSBuilder(args)

    if args.sdk.startswith("iphonesimulator"):
        app_path = ios_builder.build_app()
        print("app_path: {}".format(app_path))
        sys.exit(0)

    ipa_path = ios_builder.build_ipa()
    app_qrcode_url = upload_ipa_to_pgyer(ipa_path)
    try:
        output_folder = os.path.dirname(ipa_path)
        save_qrcode_image(app_qrcode_url, output_folder)
    except Exception as e:
        print("Exception occured: {}".format(str(e)))


if __name__ == '__main__':
    main()
