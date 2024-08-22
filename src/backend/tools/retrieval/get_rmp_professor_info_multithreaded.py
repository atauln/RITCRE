from tools.retrieval.helpers.schedule import lookup_professor

from multiprocessing import Pool
from tools.retrieval.helpers.schedule import lookup_professor
from multiprocessing import Pool

def get_rmp_professor_info_multithreaded(professor_str: list[str]) -> list[str]:
    """Get info on multiple professors from RateMyProfessor using multithreading.

    Args:
        professor_str (list[str]): The professors to get info for.

    Returns:
        list[str]: Professor ratings overview
    """

    with Pool(8) as p:
        professors = p.map(lookup_professor, professor_str)

    professor_info_arr = []
    for professor in professors:
        if professor is not None and professor.rating is not None and professor.name is not None:
            professor_info = ""
            professor_info += "%s:\n" % (professor.name)
            professor_info += "Rating: %s / 5\n" % professor.rating
            professor_info += "Difficulty: %s / 5\n" % professor.difficulty
            professor_info += "Total Ratings: %s\n" % professor.num_ratings
            if professor.would_take_again is not None:
                professor_info += "Would Take Again: %s%%\n" % round(professor.would_take_again, 1)
            else:
                professor_info += "Would Take Again: N/A\n"
            professor_info_arr.append(professor_info)
        else:
            professor_info_arr.append("Professor not found.")

    return professor_info_arr

if __name__ == '__main__':
    print(get_rmp_professor_info_multithreaded("Christian Newman"))
    