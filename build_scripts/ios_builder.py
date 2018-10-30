#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
import shutil
import plistlib
import sys


class iOSBuilder(object):
    """docstring for iOSBuilder"""
    def __init__(self, options):
        self._build_method = options.build_method
        self._sdk = options.sdk
        self._configuration = options.configuration
        self._output_folder = options.output_folder
        self._build_version_plist_path = options.build_version_plist_path
        self._export_options_plist_path = options.export_options_plist_path
        self._package_type = options.package_type
        self._archive_path = None
        self._password = options.password
        self._fabric_key = options.fabric_key
        self._env = options.env
        self._build_params = self._get_build_params(
            options.project, options.workspace, options.scheme)
        self._prepare()

    @staticmethod
    def run_shell(cmd_shell, need_result=False):
        if need_result:
            process = subprocess.Popen(cmd_shell, shell=True, stdout=subprocess.PIPE)
            process.wait()
            result_code = process.returncode
            if result_code:
                sys.exit(result_code)
            return process.stdout.read().strip()
        else:
            subprocess.check_call(cmd_shell, shell=True)

    def _get_build_params(self, project, workspace, scheme):
        build_params = None
        if project is None and workspace is None:
            raise RuntimeError("project and workspace should not both be None.")
        elif project is not None:
            build_params = '-project %s -scheme %s' % (project, scheme)
            # specify package name
            self._package_name = "{0}_{1}".format(scheme, self._configuration)
            self._app_name = scheme
        elif workspace is not None:
            build_params = '-workspace %s -scheme %s' % (workspace, scheme)
            # specify package name
            self._package_name = "{0}_{1}".format(scheme, self._configuration)
            self._app_name = scheme

        build_params += ' -sdk %s -configuration %s' % (self._sdk, self._configuration)
        return build_params

    def _prepare(self):
        """ get prepared for building.
        """
        self._change_build_number()
        self._change_method()
        # 在xcconfig中修改server环境,只对有道乐读项目有效
        self._change_server_env()

        print("Output folder for ipa ============== {}".format(self._output_folder))
        try:
            shutil.rmtree(self._output_folder)
        except OSError:
            print('{} 目录无法删除'.format(self._output_folder))
        finally:
            os.makedirs(self._output_folder)

        self._udpate_pod_dependencies()
        # 远程执行shell需要解锁keychain
        # self._unlock_keychain()
        self._build_clean()

    def _change_build_number(self):
        if self._build_version_plist_path:
            plist_list = self._build_version_plist_path.split(',')
            for plist in plist_list:
                with open(plist, 'rb') as fp:
                    plist_content = plistlib.load(fp)
                    temp = plist_content['CFBundleVersion']
                    plist_content['CFBundleVersion'] = str(int(temp) + 1)
                with open(plist, 'wb') as fp:
                    plistlib.dump(plist_content, fp)

    def _change_method(self):
        """change method in export_options_plist
        """
        plist_path = self._export_options_plist_path
        if self._package_type:
            with open(plist_path, 'rb') as fp:
                plist_content = plistlib.load(fp)
                plist_content['method'] = self._package_type
            with open(plist_path, 'wb') as fp:
                plistlib.dump(plist_content, fp)

    def _change_server_env(self):

        if self._env is not None:
            test_env = 'XCCONFIG_IS_TESTSERVER'
            pre_env = 'XCCONFIG_IS_PRERELEASE'
            test_env_yes = '{} = YES'.format(test_env)
            test_env_no = '{} = NO'.format(test_env)
            pre_env_yes = '{} = YES'.format(pre_env)
            pre_env_no = '{} = NO'.format(pre_env)
            xcconfig_path = os.path.join(os.getcwd(), 'AthenaPhone', 'Resources', 'xcconfig', '{}.xcconfig'
                                         .format(self._configuration))

            with open(xcconfig_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            with open(xcconfig_path, 'w', encoding='utf-8') as f_w:
                for line in lines:
                    if self._env == 'test':
                        if test_env_no in line:
                            line = line.replace(test_env_no, test_env_yes)
                        if pre_env_yes in line:
                            line = line.replace(pre_env_yes, pre_env_no)
                    elif self._env == 'pre':
                        if test_env_yes in line:
                            line = line.replace(test_env_yes, test_env_no)
                        if pre_env_no in line:
                            line = line.replace(pre_env_no, pre_env_yes)
                    f_w.write(line)

    def _udpate_pod_dependencies(self):
        podfile = os.path.join(os.getcwd(), 'Podfile')
        podfile_lock = os.path.join(os.getcwd(), 'Podfile.lock')
        if os.path.isfile(podfile) or os.path.isfile(podfile_lock):
            print("Update pod dependencies =============")
            cmd_shell = 'pod repo update'
            self.run_shell(cmd_shell)
            print("Install pod dependencies =============")
            cmd_shell = 'pod install'
            self.run_shell(cmd_shell)

    def _unlock_keychain(self):
        cmd_shell = 'security unlock-keychain -p {} $KEYCHAIN'.format(self._password)
        self.run_shell(cmd_shell)

    def _build_clean(self):
        cmd_shell = '{0} {1} clean'.format(self._build_method, self._build_params)
        print("build clean ============= {}".format(cmd_shell))
        self.run_shell(cmd_shell)

    def _build_archive(self):
        """ specify output xcarchive location
        """
        self._archive_path = os.path.join(
            self._output_folder, 'products', '{}.xcarchive'.format(self._package_name))
        cmd_shell = '{0} {1} archive -derivedDataPath {2} -archivePath {3}'.format(
            self._build_method, self._build_params, self._output_folder, self._archive_path)
        print("build archive ============= {}".format(cmd_shell))
        self.run_shell(cmd_shell)

    def _export_ipa(self):
        """ export archive to ipa file, return ipa location
        """
        export_path = os.path.join(self._output_folder, 'products')
        cmd_shell = 'xcodebuild -exportArchive ' \
                    '-archivePath {0} ' \
                    '-exportOptionsPlist {1} ' \
                    '-exportPath {2} ' \
                    '-allowProvisioningUpdates'\
            .format(self._archive_path, self._export_options_plist_path, export_path)
        print("build archive ============= {}".format(cmd_shell))
        self.run_shell(cmd_shell)
        ipa_path = os.path.join(export_path, '{}.ipa'.format(self._app_name))
        return ipa_path

    def _upload_dsym(self):
        if self._fabric_key:
            dsym_path = '{}/dSYMs/有道云笔记.app.dSYM'.format(self._archive_path)
            cmd_shell = 'Pods/Fabric/upload-symbols -a {0} -p ios {1}'.format(self._fabric_key, dsym_path)
            self.run_shell(cmd_shell)

    def build_ipa(self):
        """ build ipa file for iOS device
        """
        self._build_archive()
        ipa_path = self._export_ipa()
        self._upload_dsym()
        return ipa_path

    def _build_archive_for_simulator(self):
        cmd_shell = '{0} {1} -derivedDataPath {2}'.format(
            self._build_method, self._build_params, self._output_folder)
        print("build archive for simulator ============= {}".format(cmd_shell))
        self.run_shell(cmd_shell)
        app_path = os.path.join(
            self._output_folder,
            "Build",
            "Products",
            "{0}-iphonesimulator".format(self._configuration),
            "{0}.app".format(self._app_name)
        )
        return app_path

    def build_app(self):
        """ build app file for iOS simulator
        """
        app_path = self._build_archive_for_simulator()
        return app_path
