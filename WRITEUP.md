# Write-up Template

### Analyze, choose, and justify the appropriate resource option for deploying the app.

*For **both** a VM or App Service solution for the CMS app:*

- *Analyze costs, scalability, availability, and workflow*
AZURE VIRTUAL MACHINE
COST: 
    -VM instance continousluy regardless of traffic.
    -additional cost for storage, networking, operating maintenance and additional cost to upscale to a larger size if needed in the future.
Scalability:
    -Manual upsizing needed.  Requires active monitoring and intervention to increase or resize.
Availability:
    -Manual configuration needed. Increasing risk of misconfiguration.
Workflow:
    -Deploying on a VM requires managing the operating system, Python runtime, security patches, web server configuration, and application startup processes. This significantly increases operational overhead and slows development and deployment workflows.

Azure App Service
COST: 
    -Service plans selection allow for more controlled cost.  Limiting the use based on selections.
    -Costs include hosting, built‑in scaling features, and platform management, reducing the need for additional infrastructure expenses making it more cost effective for a web application like CMS.
Scalability:
    -Provides built in scaling options.  No manual intervention needed. Makes it more versatile for workloads.
Availability:
    -App Services has this built in by defaule.  Azure manages infrastructure redundancy, platform updates, and recovery, reducing the risk of downtime and eliminating the need for complex availability configurations.
Workflow:
    -Much simpler deployment workflow.  Runtime environments, terminations and process management all handled with the platform.  This would require application logic focus rather than infrastructure.

- *Choose the appropriate solution (VM or App Service) for deploying the app*
- *Justify your choice*
App Service was chosen as the deployment platform for the Article CMS application.
App Service provides a managed, scalable, and highly available environment that aligns well with the needs of a Flask‑based web application. It reduces operational complexity by eliminating the need to manage servers and operating systems, while offering built‑in scalability and availability. Additionally, App Service integrates smoothly with Azure services such as SQL Database, Blob Storage, and Azure Active Directory, making it the most efficient and maintainable solution for this project.

### Assess app changes that would change your decision.

*Detail how the app and any other needs would have to change for you to change your decision in the last section.* 

My decision would change if there were additional requirements such as full control over the underlying operatiing systems or network configurations.  If there was a need for running background proceses or if I needed to host multiple services on the same machine.  

In the cases stated above additionally specialized hardware, or custom firewall rules would make me reconsider the choice of a app service.  Dependant on the circumstances and requirements the virtual machine might be worth the increased management overhead if we needed more flexibility. 