# datasources/taiga_handler.py

from typing import Dict


def parse_taiga_event(raw_payload: Dict) -> Dict:
    """
    Parse a taiga event payload into a more detailed structure.
    """
    event_type = raw_payload.get("type")
    if event_type == "issue":       #Create issue
        return parse_taiga_issue_event(raw_payload)
    elif event_type == "epic":
        return parse_taiga_epic_event(raw_payload)

    elif event_type == "task":
        return parse_taiga_task_event(raw_payload)
    elif event_type == "userstory":
        return parse_taiga_userstory_event(raw_payload)
    elif event_type == "relateduserstory":
        return parse_taiga_related_userstory_event(raw_payload)
    else:
        return {
            "event": event_type,
            "error": "Unsupported event type"
            }




def parse_taiga_issue_event(raw_payload: Dict) -> Dict:   #if he issue is acion =change, we shpuld put the changes

    issue_id=raw_payload.get("data",{}).get("id", "")
    team_name = raw_payload.get("data",{}).get("project", {}).get("name", "")
    event_type= raw_payload.get("type","")
    action_type= raw_payload.get("action","")
    subject = raw_payload.get("data",{}).get("subject", "")
    due_date = raw_payload.get("data",{}).get("due_date", "")
    description = raw_payload.get("data", {}).get("description", "") 
    severity = raw_payload.get("data", {}).get("severity", {}).get("name", "")
    status = raw_payload.get("data", {}).get("status", {}).get("name", "")
    priority = raw_payload.get("data", {}).get("priority", {}).get("name", "")
    type = raw_payload.get("data", {}).get("type", {}).get("name", "") 
    is_closed = raw_payload.get("is_closed", False)
    modified_date = raw_payload.get("data", {}).get("modified_date", "")
    created_date = raw_payload.get("data", {}).get("created_date", "")
    finished_date = raw_payload.get("data", {}).get("finished_date", "")
    assigned_by = raw_payload.get("by", {}).get("username", "")
    #There are cases where the assigned_to field is empty, and if we request it aniways it will throw an error, so we need to check if it exists
    if raw_payload.get("data", {}).get("assigned_to", {}) != None:
        assigned_to = raw_payload.get("data", {}).get("assigned_to", {}).get("username", "")
    else:
        assigned_to = None
    

        
    doc = {
        "team_name": team_name,
        "event_type": event_type,
        "action_type": action_type,
        "issue_id": issue_id,
        "subject": subject,
        "description": description,
        "due_date": due_date,
        "severity": severity,
        "status": status,
        "priority": priority,
        "type": type,
        "is_closed": is_closed,
        "modified_date": modified_date,
        "created_date": created_date,
        "finished_date": finished_date,
        "assigned_by": assigned_by,
        "assigned_to": assigned_to
    }

    

    return doc




def parse_taiga_epic_event(raw_payload: Dict) -> Dict:   
    '''
TODO:
EL TEMA DE PROGRESS/TOTAL NO FUNCIONA. 

'''

    epic_id= raw_payload.get("data",{}).get("id", "")
    team_name = raw_payload.get("data",{}).get("project", {}).get("name", "")
    event_type= raw_payload.get("type","")
    action_type= raw_payload.get("action","")
    subject = raw_payload.get("data",{}).get("subject", "")
    status = raw_payload.get("data", {}).get("status", {}).get("name", "")
    
    progress = raw_payload.get("data", {}).get("progress", 0)           #NS que es, puede ser numero de taks or userstories
    total = raw_payload.get("data", {}).get("total", 0)                 #NS que es, puede ser numero de taks or userstories
    
    is_closed = raw_payload.get("is_closed", False)
    modified_date = raw_payload.get("data", {}).get("modified_date", "")
    created_date = raw_payload.get("data", {}).get("created_date", "")

    #We are going to use this project_id to delete the webhooks with the TAIGA API
    project_id= raw_payload.get("data",{}).get("project",{}).get("id", "")
        
    doc = {
        "epic_id": epic_id,
        "team_name": team_name,
        "event_type": event_type,
        "action_type": action_type,
        "subject": subject,
        "is_closed": is_closed,
        "status": status,
        "progress": progress,
        "total": total,
        "modified_date": modified_date,
        "created_date": created_date,
        "project_id": project_id

    }

    return doc




def parse_taiga_task_event(raw_payload: Dict) -> Dict:  #What if we delete a task?
    
    '''
    TODO:
    Get the closed_points and total Points
    '''
    #If the action type is a change, we must change the original document in mongo and update it with the new values
    team_name = raw_payload.get("data",{}).get("project", {}).get("name", "")
    event_type= raw_payload.get("type","")
    action_type= raw_payload.get("action","")
    task_id= raw_payload.get("data",{}).get("id", "")
    subject = raw_payload.get("data",{}).get("subject", "")
    userstory_id= raw_payload.get("data",{}).get("user_story",{}).get("id", "")
    is_closed = raw_payload.get("data", {}).get("status", {}).get("is_closed", "")
    status = raw_payload.get("data", {}).get("status", {}).get("name", "")
    created_date = raw_payload.get("data", {}).get("created_date", "")
    modified_date = raw_payload.get("data", {}).get("modified_date", "")
    finished_date = raw_payload.get("data", {}).get("finished_date", "")
    reference=raw_payload.get("data",{}).get("ref", "")
    milestone_id=raw_payload.get("data",{}).get("milestone",{}).get("id", "")
    milestone_name=raw_payload.get("data",{}).get("milestone",{}).get("name", "")
    milestone_closed=raw_payload.get("data",{}).get("milestone",{}).get("closed", "")
    #How can i ge these metrics¿
    #milestone_closed_points=
    #milestone_total_points=
    milestone_created_date=raw_payload.get("data",{}).get("milestone",{}).get("created_date", "")
    milestone_modified_date=raw_payload.get("data",{}).get("milestone",{}).get("modified_date", "")
    estimated_start=raw_payload.get("data",{}).get("milestone",{}).get("estimated_start", "")
    estimated_finish=raw_payload.get("data",{}).get("milestone",{}).get("estimated_finish", "")

    

    assigned_by = raw_payload.get("by", {}).get("username", "")
    
    

      
    # If we dont inizialize the metrics, when we try to delete them it shows an error 
    estimated_effort = ""
    actual_effort = ""
      
    if raw_payload.get("data", {}).get("custom_attributes_values", {}) != None:
        #Depends if the subject has hese metrics? PROBLEMA, CUANDO SE DEFINEN ESTAS METRICAS, SE TIENEN QUE PONER AQUI!
        estimated_effort=raw_payload.get("data", {}).get("custom_attributes_values", {}).get("Estimated Effort", "") #Here must be the exact name of the custom attribute
        actual_effort=raw_payload.get("data", {}).get("custom_attributes_values", {}).get("Actual Effort", "") #Here must be the exact name of the custom attribute
    else:
        assigned_to = None
        
    #If someone defines a new metric, if it isnt listed in the handler, we wont get it. To solve we can get all the custom attributes as an object and store it in mongo
    custom_attributes = raw_payload.get("data", {}).get("custom_attributes_values", {})
    if custom_attributes is None:
        custom_attributes = {}
        
        
        
        
   
    #There are cases where the assigned_to field is empty, and if we request it aniways it will throw an error, so we need to check if it exists
    if raw_payload.get("data", {}).get("assigned_to", {}) != None:
        assigned_to = raw_payload.get("data", {}).get("assigned_to", {}).get("username", "")
    else:
        assigned_to = None
    

        
    doc = {
        "team_name": team_name,
        "event_type": event_type,
        "action_type": action_type,
        "subject": subject,
        "task_id": task_id,
        "userstory_id": userstory_id,
        "is_closed": is_closed,
        "status": status,
        "assigned_to": assigned_to,
        "assigned_by": assigned_by,
        "created_date": created_date,
        "modified_date": modified_date,
        "finished_date": finished_date,
        "estimated_effort": estimated_effort,
        "actual_effort": actual_effort,
        "reference": reference,
        "milestone_id": milestone_id,
        "milestone_name": milestone_name,
        "milestone_closed": milestone_closed,
        #"milestone_closed_points": milestone_closed_points,
        #"milestone_total_points": milestone_total_points,
        "milestone_created_date": milestone_created_date,
        "milestone_modified_date": milestone_modified_date,
        "estimated_start": estimated_start,
        "estimated_finish": estimated_finish,
        
        #We can get all the custom attributes like an object, but in mongo they will have the name defined in taiga.
        "custom_attributes": custom_attributes, 
    }

    

    return doc







#Most fields dont appear when creating the user story from zero, they appear once we link it to an epic
def parse_taiga_userstory_event(raw_payload: Dict) -> Dict:   
    '''
    TODO:
    MIlestone closed points dont work
    
    '''
    userstory_id= raw_payload.get("data",{}).get("id", "")
    team_name = raw_payload.get("data",{}).get("project", {}).get("name", "")
    event_type= raw_payload.get("type","")
    action_type= raw_payload.get("action","")
    subject = raw_payload.get("data",{}).get("subject", "")
    status = raw_payload.get("data", {}).get("status", {}).get("name", "")
    is_closed = raw_payload.get("is_closed", False)
    modified_date = raw_payload.get("data", {}).get("modified_date", "")
    created_date = raw_payload.get("data", {}).get("created_date", "")
    

    
    if raw_payload.get("data",{}).get("milestone",{}) != None:
        
        milestone_id= raw_payload.get("data",{}).get("milestone",{}).get("id", "")
        milestone_name= raw_payload.get("data",{}).get("milestone",{}).get("name", "")
        milestone_closed= raw_payload.get("data",{}).get("milestone",{}).get("is_closed", "")
        
        #THESE DONT WORK
        #milestone_closed_points= raw_payload.get("data",{}).get("milestone",{}).get("points", 0)
        #milestone_total_points= raw_payload.get("data",{}).get("milestone",{}).get("total_points", 0)
        
        milestone_created_date= raw_payload.get("data",{}).get("milestone",{}).get("created_date", "")
        milestone_modified_date= raw_payload.get("data",{}).get("milestone",{}).get("modified_date", "")
        estimated_start= raw_payload.get("data",{}).get("milestone",{}).get("estimated_start", "")
        estimated_finish= raw_payload.get("data",{}).get("milestone",{}).get("estimated_finish", "")
    else:
        milestone_id= ""
        milestone_name= ""
        milestone_closed= ""
        milestone_closed_points= ""
        milestone_total_points= ""
        milestone_created_date= ""
        milestone_modified_date= ""
        estimated_start= ""
        estimated_finish= ""
    

    priority = raw_payload.get("data", {}).get("custom_attributes_values", {}).get("Priority", "")
    points_list = raw_payload.get("data",{}).get("points", [])
    sum_points = sum(p.get("value") or 0 for p in points_list)

        
    doc = {
        "team_name": team_name,
        "event_type": event_type,
        "action_type": action_type,
        "subject": subject,
        "userstory_id": userstory_id,

        "is_closed": is_closed,
        "status": status,
        
        "created_date": created_date,
        "modified_date": modified_date,
        
        "total_points": sum_points,
        # "finished_date": finished_date,
        # "assigned_to": assigned_to,
                
        "milestone_id": milestone_id,
        "milestone_name": milestone_name,
        "milestone_closed": milestone_closed,
        #"milestone_closed_points": milestone_closed_points,
        #"milestone_total_points": milestone_total_points,
        "milestone_created_date": milestone_created_date,
        "milestone_modified_date": milestone_modified_date,
        "estimated_start": estimated_start,
        "estimated_finish": estimated_finish,
        
        #"acceptance_criteria": acceptance_criteria, #TRUE IF THE USER STORY HAS ACCEPTANCE CRITERIA
        #"pattern": pattern,    #TRUE IF THE USER STORY HAS PATTERN (AS - A - I WANT - SO THAT)
        "priority": priority,
    }

    return doc




def parse_taiga_related_userstory_event(raw_payload: Dict) -> Dict:   
    #TO RELATE THE EPIC WITH A USERSTORY
    userstory_id= raw_payload.get("data",{}).get("user_story",{}).get("id", "")
    team_name = raw_payload.get("data",{}).get("epic",{}).get("project", {}).get("name", "")
    event_type= raw_payload.get("type","")
    finished_date = raw_payload.get("data",{}).get("finished_date", "")
    assigned_to = raw_payload.get("data",{}).get("assigned_to",{}).get("username", "")
    epic_id= raw_payload.get("data",{}).get("epic",{}).get("id", "")
    epic_name= raw_payload.get("data",{}).get("epic",{}).get("subject","")
    reference= raw_payload.get("data",{}).get("epic",{}).get("ref", "")

        
    doc = {
        "id": userstory_id,  
        "team_name": team_name,
        "event_type": event_type,
        "epic_id": epic_id,
        "epic_name": epic_name, 
        "reference": reference,
        "finished_date": finished_date,
        "assigned_to": assigned_to,
    }

    return doc