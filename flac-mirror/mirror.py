#!/usr/bin/python3
# -*- coding: utf-8 -*-

from os import environ
import os.path
import sys
from os import walk
import time
import subprocess

# Track files that have failed during this container's uptime
FAILED_FILES = set()

def check_mirror_status(flac_file, mirror_format):
    # 1. Ignore Apple/System metadata immediately
    if os.path.basename(flac_file).startswith('._'):
        return 'IGNORED'
    
    # 2. Check if we've already given up on this file this session
    if flac_file in FAILED_FILES:
        return 'PERSISTENT_ERROR'

    rel_name = os.path.relpath(flac_file, flac_dir)[:-5]
    mirror_file_name = os.path.join(mirror_format['DIR'], "{}.{}".format(rel_name, mirror_format['EXT'].lower()))
    
    if not os.path.isfile(mirror_file_name):
        print(f'Mirroring: {rel_name}.flac -> {mirror_format["EXT"]}', flush=True)

        mirror_dir_name = os.path.dirname(mirror_file_name)
        if not os.path.isdir(mirror_dir_name):
            os.makedirs(mirror_dir_name, exist_ok=True)
            flac_file_dir = os.path.dirname(os.path.abspath(flac_file))
            os.chown(mirror_dir_name, os.stat(flac_file_dir).st_uid, os.stat(flac_file_dir).st_gid)
            os.chmod(mirror_dir_name, os.stat(flac_file_dir).st_mode & 0o777)

        mirror_command = ['/usr/bin/ffmpeg', '-hide_banner', '-loglevel', 'error', '-i', flac_file]
        mirror_command = mirror_command + mirror_format['OPTIONS']
        mirror_command.append(mirror_file_name)
        
        result = subprocess.run(mirror_command, capture_output=True)

        if result.returncode == 0:
            if os.path.isfile(mirror_file_name):
                os.chown(mirror_file_name, os.stat(flac_file).st_uid, os.stat(flac_file).st_gid)
                os.chmod(mirror_file_name, os.stat(flac_file).st_mode & 0o777)
            print(f'Completed: {rel_name}', flush=True)
            return 'MIRRORED'
        else:
            # LOUD LOGGING for actual failures
            print(f"!!! ERROR: Failed to transcode {flac_file}", file=sys.stderr, flush=True)
            if result.stderr:
                print(f"!!! FFMPEG STDERR: {result.stderr.decode()}", file=sys.stderr, flush=True)
            
            FAILED_FILES.add(flac_file)
            return 'ERROR'

    return 'EXISTS'

def scan_flac_dir():
    counts = {'FLAC': 0}
    start_time = time.time()
    for (dirpath, dirnames, filenames) in walk(flac_dir):
        dirnames[:] = [d for d in dirnames if not d.startswith('.')]
        for f in filenames:
            if f.endswith('.flac') and not f.startswith('._'):
                counts['FLAC'] += 1
                flac_file = os.path.join(dirpath, f)

                for mirror_format in mirror_formats:
                    rc = check_mirror_status(flac_file, format_options[mirror_format])
                    cc = f"{mirror_format}_{rc}"
                    counts[cc] = counts.get(cc, 0) + 1

    # Format the task summary
    tasks = []
    for m in mirror_formats:
        new = counts.get(f"{m}_MIRRORED", 0)
        err = counts.get(f"{m}_ERROR", 0)
        tasks.append(f"{m}: {new} new, {err} fail")

    # Final heartbeat line
    log_msg = f"Heartbeat: {counts['FLAC']} total FLACs | {len(FAILED_FILES)} skipped (errors) | {', '.join(tasks)}"
    print(log_msg, flush=True)

if __name__ == "__main__":
    mirror_formats = [m for m in environ.get('MIRROR', '').strip().split(',') if m]
    flac_dir = environ.get('FLAC_DIR', '/flac')
    
    format_options = {
        'M4A': {'OPTIONS':'-c:a aac -b:a 192k -vn', 'DIR': '/m4a', 'EXT': 'm4a'},
        'MP3': {'OPTIONS':'-c:a mp3 -ab 192k -map_metadata 0', 'DIR':'/mp3', 'EXT':'mp3'},
        'OGG': {'OPTIONS':'-c:a libvorbis', 'DIR': '/ogg', 'EXT':'ogg'}
    }

    for fmat in mirror_formats:
        if fmat in format_options:
            ev_dir, ev_opt = f"{fmat}_DIR", f"{fmat}_OPTIONS"
            if ev_dir in environ: format_options[fmat]['DIR'] = environ[ev_dir]
            if ev_opt in environ: format_options[fmat]['OPTIONS'] = environ[ev_opt]
            format_options[fmat]['OPTIONS'] = format_options[fmat]['OPTIONS'].split()

    print(f"flac-mirror logic updated. Persistent errors will be logged with '!!!'.", flush=True)
    while True:
        scan_flac_dir()
        time.sleep(60)
