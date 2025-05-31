-- io.stderr:write("Current Lua version: " .. _VERSION .. "\n") 5.1

description = "Print specified fields with null checks and in JSON format"
short_description = "print fields as JSON"
category = "Custom"

local json = require ("json")
local messagepack = require ("MessagePack")

args = {}

-- 字段列表
local fields = {
    "container.id",
    "evt.arg.data",
    "evt.arg.filename",
    "evt.arg.newpath",
    "evt.arg.oldpath",
    "evt.arg.pid",
    "evt.buffer", -- 判断是否是A#t#k#F#
    "evt.category",
    "evt.datetime",
    "evt.dir",
    "evt.is_io_read",
    "evt.is_io_write",
    "evt.num",
    "evt.rawres",
    "evt.time",
    "evt.type",
    "fd.cip",
    "fd.cport",
    "fd.directory",
    "fd.ino",
    "fd.is_server",
    "fd.lip",
    "fd.name",
    "fd.num",
    "fd.rip",
    "fd.sip",
    "fd.sport",
    "fd.type",
    "proc.cmdline",
    "proc.env[malicious]",
    "proc.exepath",
    "proc.name",
    "proc.pid",
    "proc.vpid",
    "thread.tid",
    "thread.vtid",
}

-- 在这里请求字段
function on_init()
    local filename = "/tmp/capture_dir/sysdig.json"

    -- 尝试打开文件
    outfile, err = io.open(filename, "w")
    if err then
        io.stderr:write("Error opening file: " .. err .. "\n")
        return false
    end

    -- 请求需要的字段
    field_handles = {}
    for _, field in ipairs(fields) do
        table.insert(field_handles, chisel.request_field(field))
    end

    index_to_key = {}
    key_to_index = {}

    for i, field in ipairs(fields) do
        index_to_key[i] = field
        key_to_index[field] = i
    end

    io.write(messagepack.pack(index_to_key))

    return true
end

-- 安全获取字段值
function safe_field(field)
    local value = evt.field(field)
    return value or "null"
end


-- 事件处理函数
function on_event()
    local event_data = {}
    for i, field_name in ipairs(fields) do
        local value = safe_field(field_handles[i])  -- 获取字段值

        -- 处理evt.buffer
        if field_name == "evt.buffer" then
            if value:sub(1, 8) == "A#t#k#F#" then
                value = "malicious"
            else
                value = "normal"
            end
        end

        if type(field_name) ~= "string" then
            io.stderr:write("Field name is not a string: " .. type(field_name) .. "\n")
            goto continue
        end

        if type(value) == "string" then
            event_data[field_name] = value
        elseif type(value) == "number" then
            event_data[field_name] = value
        elseif type(value) == "boolean" then
            event_data[field_name] = value
        else
            io.stderr:write("Unknown type: " .. type(value) .. "\n")
        end

        ::continue::
    end

    if event_data["container.id"] ~= "host" and event_data["container.id"] ~= "" and event_data["evt.type"] ~= "setsockopt" and event_data["evt.type"] ~= "getsockopt" and event_data["evt.category"] ~= "internal" and event_data["evt.category"] ~= "unknown" and event_data["thread.tid"] ~= event_data["thread.vtid"] and event_data["thread.vtid"] ~= "null" then
        new_event_data = {}
        for key, value in pairs(event_data) do
            if value == "null" then
                value = nil
            end
            new_event_data[key_to_index[key]] = value
        end
        -- io.write(json.encode(new_event_data) .. "\n")
        io.write(messagepack.pack(new_event_data))
    end
end

function on_capture_end()
    outfile:close()
end
