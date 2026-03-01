"""Compile .po file to .mo file for NVDA addon translations."""
import struct
import os

def unescape(s):
    result = []
    i = 0
    while i < len(s):
        if s[i] == '\\' and i + 1 < len(s):
            c = s[i + 1]
            if c == 'n':
                result.append('\n')
            elif c == 't':
                result.append('\t')
            elif c == '"':
                result.append('"')
            elif c == '\\':
                result.append('\\')
            else:
                result.append(s[i])
                result.append(c)
            i += 2
        else:
            result.append(s[i])
            i += 1
    return ''.join(result)

def parse_po(po_file):
    entries = []
    current_msgid = None
    current_msgstr = None
    reading = None

    with open(po_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        if line.startswith('msgid '):
            if current_msgid is not None:
                entries.append((current_msgid, current_msgstr or ''))
            val = line[6:].strip()
            if val.startswith('"') and val.endswith('"'):
                val = val[1:-1]
            current_msgid = val
            current_msgstr = None
            reading = 'msgid'
        elif line.startswith('msgstr '):
            val = line[7:].strip()
            if val.startswith('"') and val.endswith('"'):
                val = val[1:-1]
            current_msgstr = val
            reading = 'msgstr'
        elif line.startswith('"') and line.endswith('"'):
            val = line[1:-1]
            if reading == 'msgid':
                current_msgid += val
            elif reading == 'msgstr':
                if current_msgstr is None:
                    current_msgstr = ''
                current_msgstr += val
        elif not line or line.startswith('#'):
            reading = None

    if current_msgid is not None:
        entries.append((current_msgid, current_msgstr or ''))

    return entries

def write_mo(entries, mo_file):
    # Separate metadata and real entries
    real_entries = []
    metadata = None
    for msgid, msgstr in entries:
        msgid_u = unescape(msgid)
        msgstr_u = unescape(msgstr)
        if msgid_u == '':
            metadata = msgstr_u
        elif msgstr_u:
            real_entries.append((msgid_u, msgstr_u))

    real_entries.sort(key=lambda x: x[0])

    if metadata:
        real_entries.insert(0, ('', metadata))

    n = len(real_entries)
    header_size = 7 * 4
    offsets_size = n * 2 * 4
    orig_offsets_start = header_size
    trans_offsets_start = header_size + offsets_size

    orig_strings = [e[0].encode('utf-8') for e in real_entries]
    trans_strings = [e[1].encode('utf-8') for e in real_entries]

    strings_start = header_size + 2 * offsets_size

    orig_table = []
    offset = strings_start
    for s in orig_strings:
        orig_table.append((len(s), offset))
        offset += len(s) + 1

    trans_table = []
    for s in trans_strings:
        trans_table.append((len(s), offset))
        offset += len(s) + 1

    with open(mo_file, 'wb') as f:
        f.write(struct.pack('I', 0x950412de))
        f.write(struct.pack('I', 0))
        f.write(struct.pack('I', n))
        f.write(struct.pack('I', orig_offsets_start))
        f.write(struct.pack('I', trans_offsets_start))
        f.write(struct.pack('I', 0))
        f.write(struct.pack('I', 0))

        for length, off in orig_table:
            f.write(struct.pack('II', length, off))

        for length, off in trans_table:
            f.write(struct.pack('II', length, off))

        for s in orig_strings:
            f.write(s + b'\x00')
        for s in trans_strings:
            f.write(s + b'\x00')


if __name__ == '__main__':
    base = os.path.dirname(os.path.abspath(__file__))
    po_file = os.path.join(base, 'hijriDate', 'locale', 'ar', 'LC_MESSAGES', 'nvda.po')
    mo_file = os.path.join(base, 'hijriDate', 'locale', 'ar', 'LC_MESSAGES', 'nvda.mo')
    entries = parse_po(po_file)
    write_mo(entries, mo_file)
    print(f'Compiled {po_file} -> {mo_file}')
