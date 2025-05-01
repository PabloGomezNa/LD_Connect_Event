import requests

def notify_eval_push(event_type: str,prj: str ,author_login: str , quality_model: str)-> None: 
    '''
    Function used to notify Component LD_Eval about the event that has been pushed to the database.
    '''
    event_data = {
        "event_type": event_type,
        "prj": prj,
        "author_login": author_login,  # Replace with actual author login if available
        "quality_model": quality_model,  # Replace with actual quality model if available
    }
    resp = requests.post("http://localhost:5001/api/event", json=event_data)
    print("LD_Eval responded with", resp.status_code, resp.json())

