#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import requests
import json
from ios_builder import iOSBuilder

# configuration for pgyer
_API_KEY = "7cfe4393794b3fef321df0b91b393b41"
_PGYER_UPLOAD_URL = "https://www.pgyer.com/apiv2/app/upload"


def parse_upload_result(json_result):
    print('post response: %s' % json_result)
    result_code = json_result['code']

    if result_code != 0:
        print("Upload Fail!")
        raise Exception("Reason: %s" % json_result['message'])

    print("Upload Success")
    app_qrcode_url = json_result['data']['buildQRCodeURL']
    app_shortcut_url = json_result['data']['buildShortcutUrl']
    print("appQRCodeURL: %s" % app_qrcode_url)
    print("appShortcutUrl: %s" % app_shortcut_url)
    return app_qrcode_url


def upload_ipa_to_pgyer(ipa_path):
    print("Begin to upload ipa to Pgyer: %s" % ipa_path)
    cmd_shell = u'curl --retry 3 -F "_api_key=%s" -F "file=@%s" %s' % (_API_KEY, ipa_path, _PGYER_UPLOAD_URL)
    print(cmd_shell)
    result = iOSBuilder.run_shell(cmd_shell, need_result=True)
    json_result = json.loads(result)
    app_download_page_url = parse_upload_result(json_result)
    return app_download_page_url


def save_qrcode_image(app_qrcode_url, output_folder):
    response = requests.get(app_qrcode_url)
    qr_image_file_path = os.path.join(output_folder, 'QRCode.png')
    if response.status_code == 200:
        with open(qr_image_file_path, 'wb') as f:
            f.write(response.content)
    print('Save QRCode image to file: %s' % qr_image_file_path)
