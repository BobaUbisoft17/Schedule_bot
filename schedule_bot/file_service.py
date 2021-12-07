import glob


def get_schedule_class(classname):
    return [file for file in glob.glob("schedule_bot/schedule_image/*.jpg") if classname in file]
     