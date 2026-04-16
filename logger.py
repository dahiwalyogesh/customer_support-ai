from database import insert_chat, insert_escalation


def initialize_log_files():
    """
    Kept for backwards compatibility.
    DB is now initialized in database.initialize_db().
    """
    pass


def log_chat(question, action, answer="", source="", confidence_score=""):
    insert_chat(question, action, answer, source, confidence_score)


def log_escalation(question, reason):
    insert_escalation(question, reason)