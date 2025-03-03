import sys
from kankan import kankan

if __name__ == '__main__':
    nofs_file_path = None

    args = sys.argv[1:]

    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "-nofs":
            i += 1 #不要
        elif not nofs_file_path:
            nofs_file_path = arg#没设置就默认
            i += 1
        else:
            print(f"Unknown Option: {arg}")#已设置就不要
            i += 1

    kankan(nofs_file_path)