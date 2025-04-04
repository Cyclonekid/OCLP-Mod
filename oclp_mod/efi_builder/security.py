"""
security.py: Class for handling macOS Security Patches, invocation from build.py
"""

import logging
import binascii

from . import support

from .. import constants

from ..support import utilities
from ..detections import device_probe

from ..datasets import (
    smbios_data,
    os_data
)


class BuildSecurity:
    """
    Build Library for Security Patch Support

    Invoke from build.py
    """

    def __init__(self, model: str, global_constants: constants.Constants, config: dict) -> None:
        self.model: str = model
        self.config: dict = config
        self.constants: constants.Constants = global_constants
        self.computer: device_probe.Computer = self.constants.computer

        self._build()


    def _build(self) -> None:
        """
        Kick off Security Build Process
        """

        if self.constants.sip_status is False or self.constants.custom_sip_value:
            # Work-around 12.3 bug where Electron apps no longer launch with SIP lowered
            # Unknown whether this is intended behavior or not, revisit with 12.4
            logging.info("- 向 boot-args 添加 ipc_control_port_options=0")
            self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += " ipc_control_port_options=0"
            # Adds AutoPkgInstaller for Automatic OCLP-Mod installation
            # Only install if running the GUI (AutoPkg-Assets.pkg requires the GUI)
            if self.constants.wxpython_variant is True:
                support.BuildSupport(self.model, self.constants, self.config).enable_kext("AutoPkgInstaller.kext", self.constants.autopkg_version, self.constants.autopkg_path)
            if self.constants.custom_sip_value:
                logging.info(f"- 设置 SIP 值为: {self.constants.custom_sip_value}")
                self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["csr-active-config"] = utilities.string_to_hex(self.constants.custom_sip_value.lstrip("0x"))
            elif self.constants.sip_status is False:
                logging.info("- 将 SIP 设置为允许根卷修补")
                self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["csr-active-config"] = binascii.unhexlify("03080000")

            # apfs.kext has an undocumented boot-arg that allows FileVault usage on broken APFS seals (-arv_allow_fv)
            # This is however hidden behind kern.development, thus we patch _apfs_filevault_allowed to always return true
            # Note this function was added in 11.3 (20E232, 20.4), older builds do not support this (ie. 11.2.3)
            logging.info("- 允许在根修补系统上使用 FileVault")
            support.BuildSupport(self.model, self.constants, self.config).get_item_by_kv(self.config["Kernel"]["Patch"], "Comment", "Force FileVault on Broken Seal")["Enabled"] = True
            # Lets us check in sys_patch.py if config supports FileVault
            self.config["NVRAM"]["Add"]["4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102"]["OCLP-Settings"] += " -allow_fv"

            # Patch KC UUID panics due to RSR installation
            # - Ref: https://github.com/laobamac/oclp-mod/issues/1019
            logging.info("- 启用 KC UUID 不匹配补丁")
            self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += " -nokcmismatchpanic"
            support.BuildSupport(self.model, self.constants, self.config).enable_kext("RSRHelper.kext", self.constants.rsrhelper_version, self.constants.rsrhelper_path)

        if self.constants.disable_cs_lv is True:
            # In Ventura, LV patch broke. For now, add AMFI arg
            # Before merging into mainline, this needs to be resolved
            if self.constants.disable_amfi is True:
                logging.info("- 禁用 AMFI")
                self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += " amfi=0x80"
            else:
                logging.info("- 禁用库验证")
            support.BuildSupport(self.model, self.constants, self.config).get_item_by_kv(self.config["Kernel"]["Patch"], "Comment", "Disable Library Validation Enforcement")["Enabled"] = True
            support.BuildSupport(self.model, self.constants, self.config).get_item_by_kv(self.config["Kernel"]["Patch"], "Comment", "Disable _csr_check() in _vnode_check_signature")["Enabled"] = True
            self.config["NVRAM"]["Add"]["4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102"]["OCLP-Settings"] += " -allow_amfi"
            # CSLVFixup simply patches out __RESTRICT and __restrict out of the Music.app Binary
            # Ref: https://pewpewthespells.com/blog/blocking_code_injection_on_ios_and_os_x.html
            support.BuildSupport(self.model, self.constants, self.config).enable_kext("CSLVFixup.kext", self.constants.cslvfixup_version, self.constants.cslvfixup_path)

        if self.constants.secure_status is False:
            logging.info("- 禁用 SecureBootModel")
            self.config["Misc"]["Security"]["SecureBootModel"] = "Disabled"

        if smbios_data.smbios_dictionary[self.model]["Max OS Supported"] < os_data.os_data.sonoma:
            logging.info("- 启用 AMFIPass")
            support.BuildSupport(self.model, self.constants, self.config).enable_kext("AMFIPass.kext", self.constants.amfipass_version, self.constants.amfipass_path)