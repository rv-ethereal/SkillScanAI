def analyze_skills(resume_skills: list[str], jd_skills: list[str]):
    """
    Compares resume skills and job description skills.
    Returns exact match score out of 10, matched skills, and missing skills.
    """
    # Lowercase everything for matching
    resume_set_lower = {s.lower() for s in resume_skills}
    jd_set_lower = {s.lower() for s in jd_skills}
    
    if not jd_set_lower:
        return 0.0, [], []
        
    matched_skills_lower = jd_set_lower.intersection(resume_set_lower)
    missing_skills_lower = jd_set_lower.difference(resume_set_lower)
    
    # We want to return the original casing if possible, using jd_skills as source of truth
    # Build a lookup to original casing
    jd_lookup = {s.lower(): s for s in jd_skills}
    
    matched_skills = [jd_lookup[s] for s in matched_skills_lower]
    missing_skills = [jd_lookup[s] for s in missing_skills_lower]
    
    # Calculate score out of 10
    score = round((len(matched_skills) / len(jd_set_lower)) * 10, 1)
    
    return score, matched_skills, missing_skills
