# pip install google-cloud-compute
from google.cloud import compute_v1
from google.cloud.resourcemanager_v3 import ProjectsClient
from datetime import datetime, timedelta

def list_projects() -> list:

    projects_id=[]

    for project in ProjectsClient().search_projects():
        # if project.project_id.startswith('prj-'):
        projects_id.append(project.project_id)

    return projects_id

def convert_to_kst(iso8601_str):
    # convert the given time to a datetime object
    dt = datetime.fromisoformat(iso8601_str)

    # add 17 hours to the datetime object to convert it to KST
    kst = dt + timedelta(hours=17)

    # format the datetime object to a string in the desired format
    kst_str = kst.strftime('%Y-%m-%d %H:%M:%S')

    # return the KST time string
    return kst_str

def get_list_of_lists_of_ssl_certs() -> list:
    
    # forwarding_rule_client = compute_v1.ForwardingRulesClient()
    global_forwarding_rule_client = compute_v1.GlobalForwardingRulesClient()
    target_proxy_client = compute_v1.TargetHttpsProxiesClient()
    ssl_cert_client = compute_v1.SslCertificatesClient()
    whole_ssl_list=[]

    for project in list_projects():
        # print('============project============')
        # print(project)  
        ssl_list=[]

        try:
            for gfr in global_forwarding_rule_client.list(project=project):
                # print('============gfr============')
                
                if not gfr.port_range == '443-443':
                    continue

                target_https_proxy=gfr.target.split('/')[-1]
                
                # print('============cert============')
                for cert in target_proxy_client.get(project=project, target_https_proxy=target_https_proxy).ssl_certificates:
                    cert = cert.split('/')[-1]
                    cert = ssl_cert_client.get(project=project, ssl_certificate=cert)

                    if cert.type_ == 'SELF_MANAGED':

                        ssl_list.append({'Forwarding Rule Name':gfr.name,'IP Address:Port':gfr.I_p_address+':'+gfr.port_range,'Cert Name':cert.name,'Creation Time':convert_to_kst(cert.creation_timestamp),'Expiration Time':convert_to_kst(cert.expire_time),'DNS HostNames(SSL)':cert.subject_alternative_names})

            whole_ssl_list.append([project,ssl_list])

            # break
        except:
            pass
            # print('enable api!')

    # print(whole_ssl_list)
    return whole_ssl_list

def create_markdown_table(list_of_lists_of_ssl_certs):
    # Initialize an empty string to hold the table
    table = ""

    # Loop through each sub-list in the main list
    for sublist in list_of_lists_of_ssl_certs:
        # If the sub-list is empty, ignore it and continue to the next sub-list
        if not sublist[1]:
            # table += "\n\n"
            continue
        
        table += f'h1. {sublist[0]}\n'

        # Loop through each dictionary in the sub-list
        for dictionary in sublist[1]:
            # Add a table header row for the first dictionary in the sub-list
            if sublist[1].index(dictionary) == 0:
                table += "||"
                for key in dictionary.keys():
                    table += f" {key} ||"
                table += "\n"

            # Add a table row for each dictionary in the sub-list
            table += "|"
            for value in dictionary.values():
                table += f" {value} |"
            table += "\n"

        # Add two line feeds before each sub-list to create a new line in the table
        table += "\n\n"

    return table

def ssl_put_to_confluence(body):
    pass

if __name__=="__main__":
    
    list_of_lists_of_ssl_certs = get_list_of_lists_of_ssl_certs()
    table = create_markdown_table(list_of_lists_of_ssl_certs)
    body = table
    ssl_put_to_confluence(body=table)
    print(body)


    # project='w-mantis'
    # project='push-209809'
    # cert='wemake-2023'

    # ssl_cert_client = compute_v1.SslCertificatesClient()
    # cert = ssl_cert_client.get(project=project, ssl_certificate=cert)
    # pprint(cert)