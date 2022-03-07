import glob


dict_of_schoolpath = {
    "14": "school14",
    "40": "school40",
}


async def get_schedule_class(school, classname):
    return [file for file in glob.glob("schedule_image/" + dict_of_schoolpath[school] + "/*.jpg") if classname in file]
