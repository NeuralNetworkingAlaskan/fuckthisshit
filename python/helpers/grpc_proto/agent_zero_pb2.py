# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: agent_zero.proto
# Protobuf Python Version: 6.31.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    6,
    31,
    1,
    '',
    'agent_zero.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x10\x61gent_zero.proto\x12\nagent_zero\"\xb0\x02\n\x0f\x46unctionRequest\x12\x15\n\rfunction_name\x18\x01 \x01(\t\x12\x13\n\x0bmodule_name\x18\x02 \x01(\t\x12*\n\x04\x61rgs\x18\x03 \x03(\x0b\x32\x1c.agent_zero.FunctionArgument\x12\x37\n\x06kwargs\x18\x04 \x03(\x0b\x32\'.agent_zero.FunctionRequest.KwargsEntry\x12\x10\n\x08is_async\x18\x05 \x01(\x08\x12\x17\n\x0ftimeout_seconds\x18\x06 \x01(\x05\x12\x14\n\x0c\x65xecution_id\x18\x07 \x01(\t\x1aK\n\x0bKwargsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12+\n\x05value\x18\x02 \x01(\x0b\x32\x1c.agent_zero.FunctionArgument:\x02\x38\x01\"\xa2\x01\n\x10\x46unctionArgument\x12\x16\n\x0cstring_value\x18\x01 \x01(\tH\x00\x12\x13\n\tint_value\x18\x02 \x01(\x03H\x00\x12\x15\n\x0b\x66loat_value\x18\x03 \x01(\x01H\x00\x12\x14\n\nbool_value\x18\x04 \x01(\x08H\x00\x12\x15\n\x0b\x62ytes_value\x18\x05 \x01(\x0cH\x00\x12\x14\n\njson_value\x18\x06 \x01(\tH\x00\x42\x07\n\x05value\"\xbd\x01\n\x10\x46unctionResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12,\n\x06result\x18\x02 \x01(\x0b\x32\x1c.agent_zero.FunctionArgument\x12\x15\n\rerror_message\x18\x03 \x01(\t\x12\x12\n\nerror_type\x18\x04 \x01(\t\x12\x11\n\ttraceback\x18\x05 \x01(\t\x12\x16\n\x0e\x65xecution_time\x18\x06 \x01(\x01\x12\x14\n\x0c\x65xecution_id\x18\x07 \x01(\t\"\xc0\x01\n\x16\x46unctionStreamResponse\x12\x14\n\x0c\x65xecution_id\x18\x01 \x01(\t\x12\x15\n\x0blog_message\x18\x02 \x01(\tH\x00\x12\x19\n\x0fprogress_update\x18\x03 \x01(\tH\x00\x12\x34\n\x0c\x66inal_result\x18\x04 \x01(\x0b\x32\x1c.agent_zero.FunctionResponseH\x00\x12\x17\n\rerror_message\x18\x05 \x01(\tH\x00\x42\x0f\n\rresponse_type\"\xb2\x01\n\nRFCRequest\x12\x0e\n\x06method\x18\x01 \x01(\t\x12\x0c\n\x04path\x18\x02 \x01(\t\x12\x34\n\x07headers\x18\x03 \x03(\x0b\x32#.agent_zero.RFCRequest.HeadersEntry\x12\x0c\n\x04\x62ody\x18\x04 \x01(\x0c\x12\x12\n\nrequest_id\x18\x05 \x01(\t\x1a.\n\x0cHeadersEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\"\xd3\x01\n\x0bRFCResponse\x12\x13\n\x0bstatus_code\x18\x01 \x01(\x05\x12\x35\n\x07headers\x18\x02 \x03(\x0b\x32$.agent_zero.RFCResponse.HeadersEntry\x12\x0c\n\x04\x62ody\x18\x03 \x01(\x0c\x12\x12\n\nrequest_id\x18\x04 \x01(\t\x12\x0f\n\x07success\x18\x05 \x01(\x08\x12\x15\n\rerror_message\x18\x06 \x01(\t\x1a.\n\x0cHeadersEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\"]\n\x0fReadFileRequest\x12\x11\n\tfile_path\x18\x01 \x01(\t\x12\x13\n\x0b\x62inary_mode\x18\x02 \x01(\x08\x12\x10\n\x08\x65ncoding\x18\x03 \x01(\t\x12\x10\n\x08max_size\x18\x04 \x01(\x03\"\xa1\x01\n\x10ReadFileResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x16\n\x0ctext_content\x18\x02 \x01(\tH\x00\x12\x18\n\x0e\x62inary_content\x18\x03 \x01(\x0cH\x00\x12\x15\n\rerror_message\x18\x04 \x01(\t\x12\x11\n\tfile_size\x18\x05 \x01(\x03\x12\x15\n\rfile_encoding\x18\x06 \x01(\tB\t\n\x07\x63ontent\"\xa5\x01\n\x10WriteFileRequest\x12\x11\n\tfile_path\x18\x01 \x01(\t\x12\x16\n\x0ctext_content\x18\x02 \x01(\tH\x00\x12\x18\n\x0e\x62inary_content\x18\x03 \x01(\x0cH\x00\x12\x1a\n\x12\x63reate_directories\x18\x04 \x01(\x08\x12\x13\n\x0b\x61ppend_mode\x18\x05 \x01(\x08\x12\x10\n\x08\x65ncoding\x18\x06 \x01(\tB\t\n\x07\x63ontent\"R\n\x11WriteFileResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x15\n\rerror_message\x18\x02 \x01(\t\x12\x15\n\rbytes_written\x18\x03 \x01(\x03\"9\n\x11\x44\x65leteFileRequest\x12\x11\n\tfile_path\x18\x01 \x01(\t\x12\x11\n\trecursive\x18\x02 \x01(\x08\"<\n\x12\x44\x65leteFileResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x15\n\rerror_message\x18\x02 \x01(\t\"p\n\x14ListDirectoryRequest\x12\x16\n\x0e\x64irectory_path\x18\x01 \x01(\t\x12\x11\n\trecursive\x18\x02 \x01(\x08\x12\x16\n\x0einclude_hidden\x18\x03 \x01(\x08\x12\x15\n\rfile_patterns\x18\x04 \x03(\t\"v\n\x08\x46ileInfo\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0c\n\x04path\x18\x02 \x01(\t\x12\x14\n\x0cis_directory\x18\x03 \x01(\x08\x12\x0c\n\x04size\x18\x04 \x01(\x03\x12\x15\n\rmodified_time\x18\x05 \x01(\x03\x12\x13\n\x0bpermissions\x18\x06 \x01(\t\"d\n\x15ListDirectoryResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12#\n\x05\x66iles\x18\x02 \x03(\x0b\x32\x14.agent_zero.FileInfo\x12\x15\n\rerror_message\x18\x03 \x01(\t\"&\n\x11\x46ileExistsRequest\x12\x11\n\tfile_path\x18\x01 \x01(\t\"K\n\x12\x46ileExistsResponse\x12\x0e\n\x06\x65xists\x18\x01 \x01(\x08\x12\x14\n\x0cis_directory\x18\x02 \x01(\x08\x12\x0f\n\x07is_file\x18\x03 \x01(\x08\"H\n\x16\x43reateDirectoryRequest\x12\x16\n\x0e\x64irectory_path\x18\x01 \x01(\t\x12\x16\n\x0e\x63reate_parents\x18\x02 \x01(\x08\"A\n\x17\x43reateDirectoryResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x15\n\rerror_message\x18\x02 \x01(\t\"S\n\x0fMoveFileRequest\x12\x13\n\x0bsource_path\x18\x01 \x01(\t\x12\x18\n\x10\x64\x65stination_path\x18\x02 \x01(\t\x12\x11\n\toverwrite\x18\x03 \x01(\x08\":\n\x10MoveFileResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x15\n\rerror_message\x18\x02 \x01(\t\"f\n\x0f\x43opyFileRequest\x12\x13\n\x0bsource_path\x18\x01 \x01(\t\x12\x18\n\x10\x64\x65stination_path\x18\x02 \x01(\t\x12\x11\n\toverwrite\x18\x03 \x01(\x08\x12\x11\n\trecursive\x18\x04 \x01(\x08\":\n\x10\x43opyFileResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x15\n\rerror_message\x18\x02 \x01(\t\"\x87\x02\n\x0e\x43ommandRequest\x12\x0f\n\x07\x63ommand\x18\x01 \x01(\t\x12\x0c\n\x04\x61rgs\x18\x02 \x03(\t\x12\x19\n\x11working_directory\x18\x03 \x01(\t\x12@\n\x0b\x65nvironment\x18\x04 \x03(\x0b\x32+.agent_zero.CommandRequest.EnvironmentEntry\x12\x17\n\x0ftimeout_seconds\x18\x05 \x01(\x05\x12\x16\n\x0e\x63\x61pture_output\x18\x06 \x01(\x08\x12\x14\n\x0c\x65xecution_id\x18\x07 \x01(\t\x1a\x32\n\x10\x45nvironmentEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\"\x9a\x01\n\x0f\x43ommandResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x11\n\texit_code\x18\x02 \x01(\x05\x12\x0e\n\x06stdout\x18\x03 \x01(\t\x12\x0e\n\x06stderr\x18\x04 \x01(\t\x12\x15\n\rerror_message\x18\x05 \x01(\t\x12\x16\n\x0e\x65xecution_time\x18\x06 \x01(\x01\x12\x14\n\x0c\x65xecution_id\x18\x07 \x01(\t\"\xbc\x01\n\x15\x43ommandStreamResponse\x12\x14\n\x0c\x65xecution_id\x18\x01 \x01(\t\x12\x16\n\x0cstdout_chunk\x18\x02 \x01(\tH\x00\x12\x16\n\x0cstderr_chunk\x18\x03 \x01(\tH\x00\x12\x33\n\x0c\x66inal_result\x18\x04 \x01(\x0b\x32\x1b.agent_zero.CommandResponseH\x00\x12\x17\n\rerror_message\x18\x05 \x01(\tH\x00\x42\x0f\n\rresponse_type\"!\n\rHealthRequest\x12\x10\n\x08\x64\x65tailed\x18\x01 \x01(\x08\"\xdc\x01\n\x0eHealthResponse\x12\x0f\n\x07healthy\x18\x01 \x01(\x08\x12\x0e\n\x06status\x18\x02 \x01(\t\x12\x38\n\x07\x64\x65tails\x18\x03 \x03(\x0b\x32\'.agent_zero.HealthResponse.DetailsEntry\x12\x16\n\x0euptime_seconds\x18\x04 \x01(\x01\x12\x14\n\x0cmemory_usage\x18\x05 \x01(\x03\x12\x11\n\tcpu_usage\x18\x06 \x01(\x01\x1a.\n\x0c\x44\x65tailsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\"(\n\rStatusRequest\x12\x17\n\x0finclude_metrics\x18\x01 \x01(\x08\"\x9a\x02\n\x0eStatusResponse\x12\x0c\n\x04mode\x18\x01 \x01(\t\x12\x11\n\tconnected\x18\x02 \x01(\x08\x12\x16\n\x0etotal_requests\x18\x03 \x01(\x03\x12\x1b\n\x13successful_requests\x18\x04 \x01(\x03\x12\x17\n\x0f\x66\x61iled_requests\x18\x05 \x01(\x03\x12\x1d\n\x15\x61verage_response_time\x18\x06 \x01(\x01\x12\x44\n\rconfiguration\x18\x07 \x03(\x0b\x32-.agent_zero.StatusResponse.ConfigurationEntry\x1a\x34\n\x12\x43onfigurationEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\"1\n\x0bPingRequest\x12\x0f\n\x07message\x18\x01 \x01(\t\x12\x11\n\ttimestamp\x18\x02 \x01(\x03\"j\n\x0cPingResponse\x12\x0f\n\x07message\x18\x01 \x01(\t\x12\x19\n\x11request_timestamp\x18\x02 \x01(\x03\x12\x1a\n\x12response_timestamp\x18\x03 \x01(\x03\x12\x12\n\nlatency_ms\x18\x04 \x01(\x01\x32\xcc\t\n\x10\x41gentZeroService\x12L\n\x0f\x45xecuteFunction\x12\x1b.agent_zero.FunctionRequest\x1a\x1c.agent_zero.FunctionResponse\x12Z\n\x15\x45xecuteFunctionStream\x12\x1b.agent_zero.FunctionRequest\x1a\".agent_zero.FunctionStreamResponse0\x01\x12<\n\tHandleRFC\x12\x16.agent_zero.RFCRequest\x1a\x17.agent_zero.RFCResponse\x12\x45\n\x08ReadFile\x12\x1b.agent_zero.ReadFileRequest\x1a\x1c.agent_zero.ReadFileResponse\x12H\n\tWriteFile\x12\x1c.agent_zero.WriteFileRequest\x1a\x1d.agent_zero.WriteFileResponse\x12K\n\nDeleteFile\x12\x1d.agent_zero.DeleteFileRequest\x1a\x1e.agent_zero.DeleteFileResponse\x12T\n\rListDirectory\x12 .agent_zero.ListDirectoryRequest\x1a!.agent_zero.ListDirectoryResponse\x12K\n\nFileExists\x12\x1d.agent_zero.FileExistsRequest\x1a\x1e.agent_zero.FileExistsResponse\x12Z\n\x0f\x43reateDirectory\x12\".agent_zero.CreateDirectoryRequest\x1a#.agent_zero.CreateDirectoryResponse\x12\x45\n\x08MoveFile\x12\x1b.agent_zero.MoveFileRequest\x1a\x1c.agent_zero.MoveFileResponse\x12\x45\n\x08\x43opyFile\x12\x1b.agent_zero.CopyFileRequest\x1a\x1c.agent_zero.CopyFileResponse\x12I\n\x0e\x45xecuteCommand\x12\x1a.agent_zero.CommandRequest\x1a\x1b.agent_zero.CommandResponse\x12W\n\x14\x45xecuteCommandStream\x12\x1a.agent_zero.CommandRequest\x1a!.agent_zero.CommandStreamResponse0\x01\x12\x42\n\tGetHealth\x12\x19.agent_zero.HealthRequest\x1a\x1a.agent_zero.HealthResponse\x12\x42\n\tGetStatus\x12\x19.agent_zero.StatusRequest\x1a\x1a.agent_zero.StatusResponse\x12\x39\n\x04Ping\x12\x17.agent_zero.PingRequest\x1a\x18.agent_zero.PingResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'agent_zero_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_FUNCTIONREQUEST_KWARGSENTRY']._loaded_options = None
  _globals['_FUNCTIONREQUEST_KWARGSENTRY']._serialized_options = b'8\001'
  _globals['_RFCREQUEST_HEADERSENTRY']._loaded_options = None
  _globals['_RFCREQUEST_HEADERSENTRY']._serialized_options = b'8\001'
  _globals['_RFCRESPONSE_HEADERSENTRY']._loaded_options = None
  _globals['_RFCRESPONSE_HEADERSENTRY']._serialized_options = b'8\001'
  _globals['_COMMANDREQUEST_ENVIRONMENTENTRY']._loaded_options = None
  _globals['_COMMANDREQUEST_ENVIRONMENTENTRY']._serialized_options = b'8\001'
  _globals['_HEALTHRESPONSE_DETAILSENTRY']._loaded_options = None
  _globals['_HEALTHRESPONSE_DETAILSENTRY']._serialized_options = b'8\001'
  _globals['_STATUSRESPONSE_CONFIGURATIONENTRY']._loaded_options = None
  _globals['_STATUSRESPONSE_CONFIGURATIONENTRY']._serialized_options = b'8\001'
  _globals['_FUNCTIONREQUEST']._serialized_start=33
  _globals['_FUNCTIONREQUEST']._serialized_end=337
  _globals['_FUNCTIONREQUEST_KWARGSENTRY']._serialized_start=262
  _globals['_FUNCTIONREQUEST_KWARGSENTRY']._serialized_end=337
  _globals['_FUNCTIONARGUMENT']._serialized_start=340
  _globals['_FUNCTIONARGUMENT']._serialized_end=502
  _globals['_FUNCTIONRESPONSE']._serialized_start=505
  _globals['_FUNCTIONRESPONSE']._serialized_end=694
  _globals['_FUNCTIONSTREAMRESPONSE']._serialized_start=697
  _globals['_FUNCTIONSTREAMRESPONSE']._serialized_end=889
  _globals['_RFCREQUEST']._serialized_start=892
  _globals['_RFCREQUEST']._serialized_end=1070
  _globals['_RFCREQUEST_HEADERSENTRY']._serialized_start=1024
  _globals['_RFCREQUEST_HEADERSENTRY']._serialized_end=1070
  _globals['_RFCRESPONSE']._serialized_start=1073
  _globals['_RFCRESPONSE']._serialized_end=1284
  _globals['_RFCRESPONSE_HEADERSENTRY']._serialized_start=1024
  _globals['_RFCRESPONSE_HEADERSENTRY']._serialized_end=1070
  _globals['_READFILEREQUEST']._serialized_start=1286
  _globals['_READFILEREQUEST']._serialized_end=1379
  _globals['_READFILERESPONSE']._serialized_start=1382
  _globals['_READFILERESPONSE']._serialized_end=1543
  _globals['_WRITEFILEREQUEST']._serialized_start=1546
  _globals['_WRITEFILEREQUEST']._serialized_end=1711
  _globals['_WRITEFILERESPONSE']._serialized_start=1713
  _globals['_WRITEFILERESPONSE']._serialized_end=1795
  _globals['_DELETEFILEREQUEST']._serialized_start=1797
  _globals['_DELETEFILEREQUEST']._serialized_end=1854
  _globals['_DELETEFILERESPONSE']._serialized_start=1856
  _globals['_DELETEFILERESPONSE']._serialized_end=1916
  _globals['_LISTDIRECTORYREQUEST']._serialized_start=1918
  _globals['_LISTDIRECTORYREQUEST']._serialized_end=2030
  _globals['_FILEINFO']._serialized_start=2032
  _globals['_FILEINFO']._serialized_end=2150
  _globals['_LISTDIRECTORYRESPONSE']._serialized_start=2152
  _globals['_LISTDIRECTORYRESPONSE']._serialized_end=2252
  _globals['_FILEEXISTSREQUEST']._serialized_start=2254
  _globals['_FILEEXISTSREQUEST']._serialized_end=2292
  _globals['_FILEEXISTSRESPONSE']._serialized_start=2294
  _globals['_FILEEXISTSRESPONSE']._serialized_end=2369
  _globals['_CREATEDIRECTORYREQUEST']._serialized_start=2371
  _globals['_CREATEDIRECTORYREQUEST']._serialized_end=2443
  _globals['_CREATEDIRECTORYRESPONSE']._serialized_start=2445
  _globals['_CREATEDIRECTORYRESPONSE']._serialized_end=2510
  _globals['_MOVEFILEREQUEST']._serialized_start=2512
  _globals['_MOVEFILEREQUEST']._serialized_end=2595
  _globals['_MOVEFILERESPONSE']._serialized_start=2597
  _globals['_MOVEFILERESPONSE']._serialized_end=2655
  _globals['_COPYFILEREQUEST']._serialized_start=2657
  _globals['_COPYFILEREQUEST']._serialized_end=2759
  _globals['_COPYFILERESPONSE']._serialized_start=2761
  _globals['_COPYFILERESPONSE']._serialized_end=2819
  _globals['_COMMANDREQUEST']._serialized_start=2822
  _globals['_COMMANDREQUEST']._serialized_end=3085
  _globals['_COMMANDREQUEST_ENVIRONMENTENTRY']._serialized_start=3035
  _globals['_COMMANDREQUEST_ENVIRONMENTENTRY']._serialized_end=3085
  _globals['_COMMANDRESPONSE']._serialized_start=3088
  _globals['_COMMANDRESPONSE']._serialized_end=3242
  _globals['_COMMANDSTREAMRESPONSE']._serialized_start=3245
  _globals['_COMMANDSTREAMRESPONSE']._serialized_end=3433
  _globals['_HEALTHREQUEST']._serialized_start=3435
  _globals['_HEALTHREQUEST']._serialized_end=3468
  _globals['_HEALTHRESPONSE']._serialized_start=3471
  _globals['_HEALTHRESPONSE']._serialized_end=3691
  _globals['_HEALTHRESPONSE_DETAILSENTRY']._serialized_start=3645
  _globals['_HEALTHRESPONSE_DETAILSENTRY']._serialized_end=3691
  _globals['_STATUSREQUEST']._serialized_start=3693
  _globals['_STATUSREQUEST']._serialized_end=3733
  _globals['_STATUSRESPONSE']._serialized_start=3736
  _globals['_STATUSRESPONSE']._serialized_end=4018
  _globals['_STATUSRESPONSE_CONFIGURATIONENTRY']._serialized_start=3966
  _globals['_STATUSRESPONSE_CONFIGURATIONENTRY']._serialized_end=4018
  _globals['_PINGREQUEST']._serialized_start=4020
  _globals['_PINGREQUEST']._serialized_end=4069
  _globals['_PINGRESPONSE']._serialized_start=4071
  _globals['_PINGRESPONSE']._serialized_end=4177
  _globals['_AGENTZEROSERVICE']._serialized_start=4180
  _globals['_AGENTZEROSERVICE']._serialized_end=5408
# @@protoc_insertion_point(module_scope)
