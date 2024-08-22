from tools.retrieval.helpers.schedule import lookup_professor

def get_rmp_professor_info(professor_str: str) -> str:
    """Get professor info from RateMyProfessor.

    Args:
        professor_str (str): The professor to get info for.

    Returns:
        str: Professor rating overview
    """
    professor = lookup_professor(professor_str)
    if professor is not None and professor.rating is not None and professor.name is not None:
        professor_info = ""
        professor_info += "%s works in the %s Department of %s.\n" % (professor.name, professor.department, professor.school.name)
        professor_info += "Rating: %s / 5\n" % professor.rating
        professor_info += "Difficulty: %s / 5\n" % professor.difficulty
        professor_info += "Total Ratings: %s\n" % professor.num_ratings
        if professor.would_take_again is not None:
            professor_info += "Would Take Again: %s%%\n" % round(professor.would_take_again, 1)
        else:
            professor_info += "Would Take Again: N/A\n"
        return professor_info
    return "Professor not found."

if __name__ == '__main__':
    print(get_rmp_professor_info("Christian Newman"))
    