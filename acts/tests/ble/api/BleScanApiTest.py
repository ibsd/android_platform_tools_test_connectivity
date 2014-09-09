# python3.4
# Copyright (C) 2014 The Android Open Source Project
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

"""
Test script to exercise Ble Scan Api's. This exercises all getters and
setters. This is important since there is a builder object that is immutable
after you set all attributes of each object. If this test suite doesn't pass,
then other test suites utilising Ble Scanner will also fail.
"""

# TODO: Refactor to use less code and be more effective.
# TODO: Add documentation to the refactored code.

import pprint
from queue import Empty

from base_test import BaseTestClass
from test_utils.bluetooth.ble_scan_utils import *
from test_utils.bluetooth.BleEnum import *
from test_utils.bluetooth.ble_helper_functions import BleScanResultError


class BleScanVerificationError(Exception):
  """Error in comparing BleScan results"""


class BleSetScanSettingsError(Exception):
  """Error in setting Ble Scan Settings"""


class BleSetScanFilterError(Exception):
  """Error in setting Ble Scan Settings"""


class BleScanApiTest(BaseTestClass):
  TAG = "BleScanApiTest"
  log_path = "".join([BaseTestClass.log_path,TAG,'/'])
  tests = None

  def __init__(self, controllers):
    BaseTestClass.__init__(self, self.TAG, controllers)
    self.tests = (
      "test_start_ble_scan_with_default_settings",
      "test_stop_ble_scan_default_settings",
      "test_scan_settings_callback_type_all_matches",
      "test_scan_settings_set_callback_type_first_match",
      "test_scan_settings_set_callback_type_match_lost",
      "test_scan_settings_set_invalid_callback_type",
      "test_scan_settings_set_scan_mode_low_power",
      "test_scan_settings_set_scan_mode_balanced",
      "test_scan_settings_set_scan_mode_low_latency",
      "test_scan_settings_set_invalid_scan_mode",
      "test_scan_settings_set_report_delay_millis_min",
      "test_scan_settings_set_report_delay_millis_min_plus_one",
      "test_scan_settings_set_report_delay_millis_max",
      "test_scan_settings_set_report_delay_millis_max_minus_one",
      "test_scan_settings_set_invalid_report_delay_millis_min_minus_one",
      "test_scan_settings_set_scan_result_type_full",
      "test_scan_settings_set_scan_result_type_abbreviated",
      "test_scan_settings_set_invalid_scan_result_type",
      "test_scan_filter_set_device_name",
      "test_scan_filter_set_device_name_blank",
      "test_scan_filter_set_device_name_special_chars",
      "test_scan_filter_set_device_address",
      "test_scan_filter_set_invalid_device_address_lower_case",
      "test_scan_filter_set_invalid_device_address_blank",
      "test_scan_filter_set_invalid_device_address_bad_format",
      "test_scan_filter_set_invalid_device_address_bad_address",
      "test_scan_filter_set_manufacturer_id_data",
      "test_scan_filter_set_manufacturer_id_data_mask",
      "test_scan_filter_set_manufacturer_max_id",
      "test_scan_filter_set_manufacturer_data_empty",
      "test_scan_filter_set_manufacturer_data_mask_empty",
      "test_scan_filter_set_invalid_manufacturer_min_id_minus_one",
      "test_scan_filter_set_service_uuid",
      "test_scan_filter_service_uuid_p_service",
      "test_classic_ble_scan_with_service_uuids_p",
      "test_classic_ble_scan_with_service_uuids_hr",
      "test_classic_ble_scan_with_service_uuids_empty_uuid_list",
      "test_classic_ble_scan_with_service_uuids_hr_and_p",
    )

  def _format_defaults(self, input):
    """
    Creates a dictionary of default ScanSetting and ScanFilter Values.
    :return: input: dict
    """
    if 'ScanSettings' not in input.keys():
      input['ScanSettings'] = (
        ScanSettingsCallbackType.CALLBACK_TYPE_ALL_MATCHES.value, 0,
        ScanSettingsScanMode.SCAN_MODE_LOW_POWER.value,
        ScanSettingsScanResultType.SCAN_RESULT_TYPE_FULL.value)
    if 'ScanFilterManufacturerDataId' not in input.keys():
      input['ScanFilterManufacturerDataId'] = -1
    if 'ScanFilterDeviceName' not in input.keys():
      input['ScanFilterDeviceName'] = None
    if 'ScanFilterDeviceAddress' not in input.keys():
      input['ScanFilterDeviceAddress'] = None
    if 'ScanFilterManufacturerData' not in input.keys():
      input['ScanFilterManufacturerData'] = ""
    return input

  def validate_scan_settings_helper(self, input, droid):
    """
    Validates each input of the scan settings object that is matches what was
    set or not set such that it matches the defaults.
    :return: False at any point something doesn't match. True if everything
    matches.
    """
    filter_list = droid.genFilterList()
    if 'ScanSettings' in input.keys():
      try:
        droid.setScanSettings(input['ScanSettings'][0],
                              input['ScanSettings'][1],
                              input['ScanSettings'][2],
                              input['ScanSettings'][3])
      except android.SL4AAPIError as error:
        self.log.debug(" ".join(["Set Scan Settings failed with:",str(error)]))
        return False
    if 'ScanFilterDeviceName' in input.keys():
      try:
        droid.setScanFilterDeviceName(input['ScanFilterDeviceName'])
      except android.SL4AAPIError as error:
        self.log.debug(" ".join(["Set Scan Filter Device Name failed with:",str(error)]))
        return False
    if 'ScanFilterDeviceAddress' in input.keys():
      try:
        droid.setScanFilterDeviceAddress(
          input['ScanFilterDeviceAddress'])
      except android.SL4AAPIError as error:
        self.log.debug(" ".join(["Set Scan Filter Device Address failed with:",str(error)]))
        return False
    if ('ScanFilterManufacturerDataId' in input.keys()
        and 'ScanFilterManufacturerDataMask' in input.keys()):
      try:
        droid.setScanFilterManufacturerData(
          input['ScanFilterManufacturerDataId'],
          input['ScanFilterManufacturerData'],
          input['ScanFilterManufacturerDataMask'])
      except android.SL4AAPIError as error:
        self.log.debug(" ".join(["Set Scan Filter Manufacturer info with data mask failed with:",
                                 str(error)]))
        return False
    if ('ScanFilterManufacturerDataId' in input.keys()
        and 'ScanFilterManufacturerData' in input.keys()
        and 'ScanFilterManufacturerDataMask' not in input.keys()):
      try:
        droid.setScanFilterManufacturerData(
          input['ScanFilterManufacturerDataId'],
          input['ScanFilterManufacturerData'])
      except android.SL4AAPIError as error:
        self.log.debug(" ".join(["Set Scan Filter Manufacturer info failed with: ",str(error)]))
        return False
    if 'ScanFilterServiceUuid' in input.keys() and 'ScanFilterServiceMask' in input.keys():
      droid.setScanFilterServiceUuid(input['ScanFilterServiceUuid'],
                                     input['ScanFilterServiceMask'])

    input = self._format_defaults(input)
    scan_settings_index = droid.buildScanSetting()
    scan_settings = (droid.getScanSettingsCallbackType(scan_settings_index),
                     droid.getScanSettingsReportDelayMillis(
                       scan_settings_index),
                     droid.getScanSettingsScanMode(scan_settings_index),
                     droid.getScanSettingsScanResultType(
                       scan_settings_index))

    scan_filter_index = droid.buildScanFilter(filter_list)
    device_name_filter = droid.getScanFilterDeviceName(filter_list, scan_filter_index)
    device_address_filter = droid.getScanFilterDeviceAddress(filter_list, scan_filter_index)
    manufacturer_id = droid.getScanFilterManufacturerId(filter_list, scan_filter_index)
    manufacturer_data = droid.getScanFilterManufacturerData(filter_list, scan_filter_index)

    if scan_settings != input['ScanSettings']:
      self.log.debug(" ".join(["Scan Settings did not match. expected:",input['ScanSettings'],
                               ", found:",str(scan_settings)]))
      return False
    if device_name_filter != input['ScanFilterDeviceName']:
      self.log.debug(" ".join(["Scan Filter device name did not match. expected:",
                               input['ScanFilterDeviceName'],", found:",device_name_filter]))
      return False
    if device_address_filter != input['ScanFilterDeviceAddress']:
      self.log.debug(" ".join(["Scan Filter address name did not match. expected:",
                               input['ScanFilterDeviceAddress'],", found: ",device_address_filter]))
      return False
    if manufacturer_id != input['ScanFilterManufacturerDataId']:
      self.log.debug(" ".join(["Scan Filter manufacturer data id did not match. expected:",
                              input['ScanFilterManufacturerDataId'],", found:",manufacturer_id]))
      return False
    if manufacturer_data != input['ScanFilterManufacturerData']:
      self.log.debug(" ".join(["Scan Filter manufacturer data did not match. expected:",
                               input['ScanFilterManufacturerData'],", found:",manufacturer_data]))
      return False
    if 'ScanFilterManufacturerDataMask' in input.keys():
      manufacturer_data_mask = droid.getScanFilterManufacturerDataMask(
        filter_list,
        scan_filter_index)
      if manufacturer_data_mask != input[
        'ScanFilterManufacturerDataMask']:
        self.log.debug(" ".join(["Manufacturer data mask did not match. expected:",
                                 input['ScanFilterManufacturerDataMask'],", found:",
                                 manufacturer_data_mask]))
        return False
    if 'ScanFilterServiceUuid' in input.keys() and 'ScanFilterServiceMask' in input.keys():
      expected_service_uuid = input['ScanFilterServiceUuid']
      expected_service_mask = input['ScanFilterServiceMask']
      service_uuid = droid.getScanFilterServiceUuid(filter_list,
                                                    scan_filter_index)
      service_mask = droid.getScanFilterServiceUuidMask(filter_list,
                                                        scan_filter_index)
      if service_uuid != expected_service_uuid.lower():
        self.log.debug(" ".join(["Service uuid did not match. expected:",expected_service_uuid,
          ", found: ",service_uuid]))
        return False
      if service_mask != expected_service_mask.lower():
        self.log.debug(" ".join(["Service mask did not match. expected: ",expected_service_mask,
                                 ", found: ",service_mask]))
        return False
    self.scan_settings_index = scan_settings_index
    self.filter_list = filter_list
    self.scan_callback = droid.genScanCallback()
    return True

  def test_start_ble_scan_with_default_settings(self):
    """
    Test to validate all default scan settings values.
    :return: bool
    """
    input = {}
    return self.validate_scan_settings_helper(input, self.droid)

  def test_stop_ble_scan_default_settings(self):
    """
    Test default scan settings on an actual scan. Verify it can also stop the
    scan.
    Steps:
    1. Validate default scan settings.
    2. Start ble scan.
    3. Stop ble scan.
    :return: test_result: bool
    """
    input = {}
    test_result = self.validate_scan_settings_helper(input, self.droid)
    if not test_result:
      self.log.debug("Could not setup ble scanner.")
      return test_result
    self.droid.startBleScan(self.filter_list,self.scan_settings_index,
                                        self.scan_callback)
    try:
      self.droid.stopBleScan(self.scan_callback)
    except BleScanResultError as error:
      self.log.debug(str(error))
      test_result = False
    return test_result

  def test_scan_settings_callback_type_all_matches(self):
    """
    Test scan settings callback type all matches.
    Steps:
    1. Validate the scan settings callback type with all other settings set to
    their respective defaults.
    :return: bool
    """
    input = {}
    input["ScanSettings"] = (
      ScanSettingsCallbackType.CALLBACK_TYPE_ALL_MATCHES.value, 0,
      ScanSettingsScanMode.SCAN_MODE_LOW_POWER.value,
      ScanSettingsScanResultType.SCAN_RESULT_TYPE_FULL.value)
    return self.validate_scan_settings_helper(input, self.droid)

  def test_scan_settings_set_callback_type_first_match(self):
    """
    Test scan settings callback type first lost.
    Steps:
    1. Validate the scan settings callback type with all other settings set to
    their respective defaults.
    :return: bool
    """
    input = {}
    input["ScanSettings"] = (
      ScanSettingsCallbackType.CALLBACK_TYPE_FIRST_MATCH.value, 0,
      ScanSettingsScanMode.SCAN_MODE_LOW_POWER.value,
      ScanSettingsScanResultType.SCAN_RESULT_TYPE_FULL.value)
    test_result = self.validate_scan_settings_helper(input, self.droid)
    return test_result

  def test_scan_settings_set_callback_type_match_lost(self):
    """
    Test scan settings callback type match lost.
    Steps:
    1. Validate the scan settings callback type with all other settings set to
    their respective defaults.
    :return: bool
    """
    input = {}
    input["ScanSettings"] = (
      ScanSettingsCallbackType.CALLBACK_TYPE_MATCH_LOST.value, 0,
      ScanSettingsScanMode.SCAN_MODE_LOW_POWER.value,
      ScanSettingsScanResultType.SCAN_RESULT_TYPE_FULL.value)
    test_result = self.validate_scan_settings_helper(input, self.droid)
    return test_result

  def test_scan_settings_set_invalid_callback_type(self):
    """
    Test scan settings invalid callback type -1.
    Steps:
    1. Validate the scan settings callback type with all other settings set to
    their respective defaults.
    :return: bool
    """
    input = {}
    input["ScanSettings"] = (
      -1, 0, ScanSettingsScanMode.SCAN_MODE_LOW_POWER.value,
      ScanSettingsScanResultType.SCAN_RESULT_TYPE_FULL.value)
    test_result = self.validate_scan_settings_helper(input, self.droid)
    return not test_result

  def test_scan_settings_set_scan_mode_low_power(self):
    """
    Test scan settings scan mode low power.
    Steps:
    1. Validate the scan settings scan mode with all other settings set to
    their respective defaults.
    :return: bool
    """
    input = {}
    input["ScanSettings"] = (
      ScanSettingsCallbackType.CALLBACK_TYPE_ALL_MATCHES.value, 0,
      ScanSettingsScanMode.SCAN_MODE_LOW_POWER.value,
      ScanSettingsScanResultType.SCAN_RESULT_TYPE_FULL.value)
    test_result = self.validate_scan_settings_helper(input, self.droid)
    return test_result

  def test_scan_settings_set_scan_mode_balanced(self):
    """
    Test scan settings scan mode balanced.
    Steps:
    1. Validate the scan settings scan mode with all other settings set to
    their respective defaults.
    :return: bool
    """
    input = {}
    input["ScanSettings"] = (
      ScanSettingsCallbackType.CALLBACK_TYPE_ALL_MATCHES.value, 0,
      ScanSettingsScanMode.SCAN_MODE_BALANCED.value,
      ScanSettingsScanResultType.SCAN_RESULT_TYPE_FULL.value)
    return self.validate_scan_settings_helper(input, self.droid)

  def test_scan_settings_set_scan_mode_low_latency(self):
    """
    Test scan settings scan mode low latency.
    Steps:
    1. Validate the scan settings scan mode with all other settings set to
    their respective defaults.
    :return: bool
    """
    input = {}
    input["ScanSettings"] = (
      ScanSettingsCallbackType.CALLBACK_TYPE_ALL_MATCHES.value, 0,
      ScanSettingsScanMode.SCAN_MODE_LOW_LATENCY.value,
      ScanSettingsScanResultType.SCAN_RESULT_TYPE_FULL.value)
    return self.validate_scan_settings_helper(input, self.droid)

  def test_scan_settings_set_invalid_scan_mode(self):
    """
    Test scan settings invalid scan mode -1.
    Steps:
    1. Validate the scan settings scan mode with all other settings set to
    their respective defaults.
    :return: bool
    """
    input = {}
    input["ScanSettings"] = (
      ScanSettingsCallbackType.CALLBACK_TYPE_ALL_MATCHES.value, 0, -1,
      ScanSettingsScanResultType.SCAN_RESULT_TYPE_FULL.value)
    return not self.validate_scan_settings_helper(input, self.droid)

  def test_scan_settings_set_report_delay_millis_min(self):
    """
    Test scan settings report delay millis min value.
    Steps:
    1. Validate the scan settings report delay millis with all other settings
    set to their respective defaults.
    :return: bool
    """
    input = {}
    input["ScanSettings"] = (
      ScanSettingsCallbackType.CALLBACK_TYPE_ALL_MATCHES.value,
      ScanSettingsReportDelaySeconds.MIN.value,
      ScanSettingsScanMode.SCAN_MODE_LOW_POWER.value,
      ScanSettingsScanResultType.SCAN_RESULT_TYPE_FULL.value)
    return self.validate_scan_settings_helper(input, self.droid)

  def test_scan_settings_set_report_delay_millis_min_plus_one(self):
    """
    Test scan settings report delay millis min value + 1.
    Steps:
    1. Validate the scan settings report delay millis with all other settings
    set to their respective defaults.
    :return: bool
    """
    input = {}
    input["ScanSettings"] = (
      ScanSettingsCallbackType.CALLBACK_TYPE_ALL_MATCHES.value,
      ScanSettingsReportDelaySeconds.MIN.value + 1,
      ScanSettingsScanMode.SCAN_MODE_LOW_POWER.value,
      ScanSettingsScanResultType.SCAN_RESULT_TYPE_FULL.value)
    return self.validate_scan_settings_helper(input, self.droid)

  def test_scan_settings_set_report_delay_millis_max(self):
    """
    Test scan settings report delay millis max value.
    Steps:
    1. Validate the scan settings report delay millis with all other settings
    set to their respective defaults.
    :return: bool
    """
    input = {}
    input["ScanSettings"] = (
      ScanSettingsCallbackType.CALLBACK_TYPE_ALL_MATCHES.value,
      ScanSettingsReportDelaySeconds.MAX.value,
      ScanSettingsScanMode.SCAN_MODE_LOW_POWER.value,
      ScanSettingsScanResultType.SCAN_RESULT_TYPE_FULL.value)
    return self.validate_scan_settings_helper(input, self.droid)

  def test_scan_settings_set_report_delay_millis_max_minus_one(self):
    """
    Test scan settings report delay millis max value - 1.
    Steps:
    1. Validate the scan settings report delay millis with all other settings
    set to their respective defaults.
    :return: bool
    """
    input = {}
    input["ScanSettings"] = (
      ScanSettingsCallbackType.CALLBACK_TYPE_ALL_MATCHES.value,
      ScanSettingsReportDelaySeconds.MAX.value - 1,
      ScanSettingsScanMode.SCAN_MODE_LOW_POWER.value,
      ScanSettingsScanResultType.SCAN_RESULT_TYPE_FULL.value)
    return self.validate_scan_settings_helper(input, self.droid)

  def test_scan_settings_set_invalid_report_delay_millis_min_minus_one(self):
    """
    Test scan settings invalid report delay millis min value - 1.
    Steps:
    1. Validate the scan settings report delay millis with all other settings
    set to their respective defaults.
    :return: bool
    """
    droid = self.droid
    input = {}
    input["ScanSettings"] = (
      ScanSettingsCallbackType.CALLBACK_TYPE_ALL_MATCHES.value,
      ScanSettingsReportDelaySeconds.MIN.value - 1,
      ScanSettingsScanMode.SCAN_MODE_LOW_POWER.value,
      ScanSettingsScanResultType.SCAN_RESULT_TYPE_FULL.value)
    return not self.validate_scan_settings_helper(input, droid)

  def test_scan_settings_set_scan_result_type_full(self):
    """
    Test scan settings result type full.
    Steps:
    1. Validate the scan settings result type with all other settings
    set to their respective defaults.
    :return: bool
    """
    input = {}
    input["ScanSettings"] = (
      ScanSettingsCallbackType.CALLBACK_TYPE_ALL_MATCHES.value, 0,
      ScanSettingsScanMode.SCAN_MODE_LOW_POWER.value,
      ScanSettingsScanResultType.SCAN_RESULT_TYPE_FULL.value)
    return self.validate_scan_settings_helper(input, self.droid)

  def test_scan_settings_set_scan_result_type_abbreviated(self):
    """
    Test scan settings result type abbreviated.
    Steps:
    1. Validate the scan settings result type with all other settings
    set to their respective defaults.
    :return: bool
    """
    input = {}
    input["ScanSettings"] = (
      ScanSettingsCallbackType.CALLBACK_TYPE_ALL_MATCHES.value, 0,
      ScanSettingsScanMode.SCAN_MODE_LOW_POWER.value,
      ScanSettingsScanResultType.SCAN_RESULT_TYPE_ABBREVIATED.value)
    return self.validate_scan_settings_helper(input, self.droid)

  def test_scan_settings_set_invalid_scan_result_type(self):
    """
    Test scan settings invalid result type -1.
    Steps:
    1. Validate the scan settings result type with all other settings
    set to their respective defaults.
    :return: bool
    """
    input = {}
    input["ScanSettings"] = (
      ScanSettingsCallbackType.CALLBACK_TYPE_ALL_MATCHES.value, 0,
      ScanSettingsScanMode.SCAN_MODE_LOW_POWER.value, -1)
    return not self.validate_scan_settings_helper(input, self.droid)

  def test_scan_filter_set_device_name(self):
    """
    Test scan filter device name sl4atest.
    Steps:
    1. Validate the scan filter device name with all other settings
    set to their respective defaults.
    :return: bool
    """
    input = {}
    input['ScanFilterDeviceName'] = "sl4atest"
    return self.validate_scan_settings_helper(input, self.droid)

  def test_scan_filter_set_device_name_blank(self):
    """
    Test scan filter device name blank.
    Steps:
    1. Validate the scan filter device name with all other settings
    set to their respective defaults.
    :return: bool
    """
    droid = self.droid
    input = {}
    input['ScanFilterDeviceName'] = ""
    return self.validate_scan_settings_helper(input, droid)

  def test_scan_filter_set_device_name_special_chars(self):
    """
    Test scan filter device name special characters.
    Steps:
    1. Validate the scan filter device name with all other settings
    set to their respective defaults.
    :return: bool
    """
    input = {}
    input['ScanFilterDeviceName'] = "!@#$%^&*()\":<>/"
    return self.validate_scan_settings_helper(input, self.droid)

  def test_scan_filter_set_device_address(self):
    """
    Test scan filter device address valid.
    Steps:
    1. Validate the scan filter device address with all other settings
    set to their respective defaults.
    :return: bool
    """
    input = {}
    input['ScanFilterDeviceAddress'] = "01:02:03:AB:CD:EF"
    return self.validate_scan_settings_helper(input, self.droid)

  def test_scan_filter_set_invalid_device_address_lower_case(self):
    """
    Test scan filter device address lower case.
    Steps:
    1. Validate the scan filter device address with all other settings
    set to their respective defaults.
    :return: bool
    """
    input = {}
    input['ScanFilterDeviceAddress'] = "01:02:03:ab:cd:ef"
    return not self.validate_scan_settings_helper(input, self.droid)

  def test_scan_filter_set_invalid_device_address_blank(self):
    """
    Test scan filter invalid device address blank.
    Steps:
    1. Validate the scan filter device address with all other settings
    set to their respective defaults.
    :return: bool
    """
    input = {}
    input['ScanFilterDeviceAddress'] = ""
    test_result = self.validate_scan_settings_helper(input, self.droid)
    return not test_result

  def test_scan_filter_set_invalid_device_address_bad_format(self):
    """
    Test scan filter invalid device address bad format.
    Steps:
    1. Validate the scan filter device address with all other settings
    set to their respective defaults.
    :return: bool
    """
    input = {}
    input['ScanFilterDeviceAddress'] = "10.10.10.10.10"
    return not self.validate_scan_settings_helper(input, self.droid)

  def test_scan_filter_set_invalid_device_address_bad_address(self):
    """
    Test scan filter invalid device address invalid characters.
    Steps:
    1. Validate the scan filter device address with all other settings
    set to their respective defaults.
    :return: bool
    """
    input = {}
    input['ScanFilterDeviceAddress'] = "ZZ:ZZ:ZZ:ZZ:ZZ:ZZ"
    return not self.validate_scan_settings_helper(input, self.droid)

  def test_scan_filter_set_manufacturer_id_data(self):
    """
    Test scan filter manufacturer data.
    Steps:
    1. Validate the scan filter manufacturer id with all other settings
    set to their respective defaults.
    :return: bool
    """
    expected_manufacturer_id = 0
    expected_manufacturer_data = "1,2,1,3,4,5,6"
    input = {}
    input['ScanFilterManufacturerDataId'] = expected_manufacturer_id
    input['ScanFilterManufacturerData'] = expected_manufacturer_data
    return self.validate_scan_settings_helper(input, self.droid)

  def test_scan_filter_set_manufacturer_id_data_mask(self):
    """
    Test scan filter manufacturer data with data mask.
    Steps:
    1. Validate the scan filter manufacturer id with all other settings
    set to their respective defaults.
    :return: bool
    """
    expected_manufacturer_id = 1
    expected_manufacturer_data = "1"
    expected_manufacturer_data_mask = "1,2,1,3,4,5,6"
    input = {}
    input['ScanFilterManufacturerDataId'] = expected_manufacturer_id
    input['ScanFilterManufacturerData'] = expected_manufacturer_data
    input[
      'ScanFilterManufacturerDataMask'] = expected_manufacturer_data_mask
    return self.validate_scan_settings_helper(input, self.droid)

  def test_scan_filter_set_manufacturer_max_id(self):
    """
    Test scan filter manufacturer data max id
    Steps:
    1. Validate the scan filter manufacturer id with all other settings
    set to their respective defaults.
    :return: bool
    """
    expected_manufacturer_id = 2147483647
    expected_manufacturer_data = "1,2,1,3,4,5,6"
    input = {}
    input['ScanFilterManufacturerDataId'] = expected_manufacturer_id
    input['ScanFilterManufacturerData'] = expected_manufacturer_data
    return self.validate_scan_settings_helper(input, self.droid)

  def test_scan_filter_set_manufacturer_data_empty(self):
    """
    Test scan filter manufacturer data empty.
    Steps:
    1. Validate the scan filter manufacturer id with all other settings
    set to their respective defaults.
    :return: bool
    """
    expected_manufacturer_id = 1
    expected_manufacturer_data = ""
    input = {}
    input['ScanFilterManufacturerDataId'] = expected_manufacturer_id
    input['ScanFilterManufacturerData'] = expected_manufacturer_data
    return self.validate_scan_settings_helper(input, self.droid)

  def test_scan_filter_set_manufacturer_data_mask_empty(self):
    """
    Test scan filter manufacturer mask empty.
    Steps:
    1. Validate the scan filter manufacturer id with all other settings
    set to their respective defaults.
    :return: bool
    """
    expected_manufacturer_id = 1
    expected_manufacturer_data = "1,2,1,3,4,5,6"
    expected_manufacturer_data_mask = ""
    input = {}
    input['ScanFilterManufacturerDataId'] = expected_manufacturer_id
    input['ScanFilterManufacturerData'] = expected_manufacturer_data
    input[
      'ScanFilterManufacturerDataMask'] = expected_manufacturer_data_mask
    return self.validate_scan_settings_helper(input, self.droid)

  def test_scan_filter_set_invalid_manufacturer_min_id_minus_one(self):
    """
    Test scan filter invalid manufacturer id min value - 1.
    Steps:
    1. Validate the scan filter manufacturer id with all other settings
    set to their respective defaults.
    :return: bool
    """
    expected_manufacturer_id = -1
    expected_manufacturer_data = "1,2,1,3,4,5,6"
    input = {}
    input['ScanFilterManufacturerDataId'] = expected_manufacturer_id
    input['ScanFilterManufacturerData'] = expected_manufacturer_data
    return not self.validate_scan_settings_helper(input, self.droid)

  def test_scan_filter_set_service_uuid(self):
    """
    Test scan filter service uuid.
    Steps:
    1. Validate the scan filter service uuid with all other settings
    set to their respective defaults.
    :return: bool
    """
    expected_service_uuid = "00000000-0000-1000-8000-00805F9B34FB"
    expected_service_mask = "00000000-0000-1000-8000-00805F9B34FB"
    input = {}
    input['ScanFilterServiceUuid'] = expected_service_uuid
    input['ScanFilterServiceMask'] = expected_service_mask
    return self.validate_scan_settings_helper(input, self.droid)

  def test_scan_filter_service_uuid_p_service(self):
    """
    Test scan filter service uuid p service
    Steps:
    1. Validate the scan filter service uuid with all other settings
    set to their respective defaults.
    :return: bool
    """
    expected_service_uuid = Uuids.P_Service.value
    expected_service_mask = "00000000-0000-1000-8000-00805F9B34FB"
    self.log.debug("Step 1: Setup environment.")

    input = {}
    input['ScanFilterServiceUuid'] = expected_service_uuid
    input['ScanFilterServiceMask'] = expected_service_mask
    return self.validate_scan_settings_helper(input, self.droid)

  def test_classic_ble_scan_with_service_uuids_p(self):
    """
    Test classic ble scan with scan filter service uuid p service uuids
    Steps:
    1. Validate the scan filter service uuid with all other settings
    set to their respective defaults.
    2. Start classic ble scan.
    3. Stop classic ble scan
    :return: bool
    """

    droid = self.droid
    service_uuid_list = [Uuids.P_Service.value]
    scan_callback = droid.genLeScanCallback()
    return verify_classic_ble_scan_with_service_uuids(self, droid, self.ed,
                                                      scan_callback,
                                                      service_uuid_list)

  def test_classic_ble_scan_with_service_uuids_hr(self):
    """
    Test classic ble scan with scan filter service uuid hr service
    Steps:
    1. Validate the scan filter service uuid with all other settings
    set to their respective defaults.
    2. Start classic ble scan.
    3. Stop classic ble scan
    :return: bool
    """
    droid = self.droid
    service_uuid_list = [Uuids.HR_SERVICE.value]
    scan_callback = droid.genLeScanCallback()
    return verify_classic_ble_scan_with_service_uuids(self, droid, self.ed,
                                                      scan_callback,
                                                      service_uuid_list)

  def test_classic_ble_scan_with_service_uuids_empty_uuid_list(self):
    """
    Test classic ble scan with service uuids as empty list
    Steps:
    1. Validate the scan filter service uuid with all other settings
    set to their respective defaults.
    2. Start classic ble scan.
    3. Stop classic ble scan
    :return: bool
    """
    droid = self.droid
    service_uuid_list = []
    scan_callback = droid.genLeScanCallback()
    return verify_classic_ble_scan_with_service_uuids(self, droid, self.ed,
                                                      scan_callback,
                                                      service_uuid_list)

  def test_classic_ble_scan_with_service_uuids_hr_and_p(self):
    """
    Test classic ble scan with service uuids a list of hr and p service
    Steps:
    1. Validate the scan filter service uuid with all other settings
    set to their respective defaults.
    2. Start classic ble scan.
    3. Stop classic ble scan
    :return: bool
    """
    droid = self.droid
    service_uuid_list = [Uuids.HR_SERVICE.value, Uuids.P_Service.value]
    scan_callback = droid.genLeScanCallback()
    return verify_classic_ble_scan_with_service_uuids(self, droid, self.ed,
                                                      scan_callback,
                                                      service_uuid_list)