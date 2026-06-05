# -*- coding: utf-8 -*-
import json

# Define the data structure for the 142 controls
controls = []

def to_title_case(s):
    exceptions = ["for", "and", "of", "in", "with", "to", "on", "from", "after", "or", "by", "against", "about"]
    # Handle parenthesized terms if any
    parts = s.split(" ")
    title_parts = []
    for idx, p in enumerate(parts):
        # Strip parentheses for exception checking but preserve in output
        clean_p = p.replace("(", "").replace(")", "").lower()
        if idx == 0 or idx == len(parts) - 1 or clean_p not in exceptions:
            # Capitalize while preserving parentheses
            if p.startswith("("):
                title_parts.append("(" + p[1:].capitalize())
            else:
                title_parts.append(p.capitalize())
        else:
            title_parts.append(p.lower())
    return " ".join(title_parts)

# --- ISO 27001:2022 A.5 (sl 1 to 37) ---
a5_controls = [
    ("Policies for information security", "📄", "Verify if information security policies are defined, approved, and communicated.", "Approved Information Security Policy Document.", ["Risk Assessment"], "HIGH"),
    ("Information security roles and responsibilities", "👥", "Verify that information security roles and responsibilities are defined and allocated.", "Org chart, role descriptions with security duties.", ["Risk Assessment"], "MEDIUM"),
    ("Segregation of duties", "🔀", "Verify that conflicting duties and areas of responsibility are segregated.", "Segregation of duties matrix, authorization logs.", ["Risk Assessment"], "HIGH"),
    ("Management responsibilities", "👔", "Verify management requires employees to apply security in accordance with established policies.", "Management meeting minutes, policy sign-offs.", ["Risk Assessment"], "MEDIUM"),
    ("Contact with authorities", "📞", "Verify that contact with relevant authorities is maintained.", "Procedure for contacting authorities, contact list.", ["Risk Assessment"], "LOW"),
    ("Contact with special interest groups", "🤝", "Verify contact with special interest groups or security associations is maintained.", "List of memberships, participation records.", ["Risk Assessment"], "LOW"),
    ("Threat intelligence", "📡", "Verify that threat intelligence is collected, analyzed, and acted upon.", "Threat intelligence feeds, vulnerability reports, actions taken.", ["Risk Assessment"], "MEDIUM"),
    ("Information security in project management", "🏗️", "Verify information security is integrated into project management.", "Project planning docs, security requirements in projects.", ["Risk Assessment"], "MEDIUM"),
    ("Inventory of information and other associated assets", "📋", "Verify that an inventory of information and other associated assets is maintained.", "Asset inventory register.", ["Asset Management"], "HIGH"),
    ("Acceptable use of information and other associated assets", "💻", "Verify that rules for acceptable use of assets are defined and implemented.", "Acceptable Use Policy (AUP) signed by employees.", ["Asset Management"], "MEDIUM"),
    ("Return of assets", "🔄", "Verify that employees and external users return all assets upon termination.", "Offboarding checklist, asset return logs.", ["Asset Management"], "MEDIUM"),
    ("Classification of information", "🏷️", "Verify that information is classified in accordance with security requirements.", "Data Classification Policy, classified document samples.", ["Data Protection & Privacy"], "HIGH"),
    ("Labelling of information", "🏷️", "Verify that procedures for labelling information are developed and implemented.", "Information labelling guidelines, screenshots of labelled data.", ["Data Protection & Privacy"], "MEDIUM"),
    ("Information transfer", "📤", "Verify that rules, procedures, and agreements for information transfer are in place.", "Data Transfer Policy, secure transfer logs, NDAs.", ["Data Protection & Privacy"], "HIGH"),
    ("Access control", "🔐", "Verify rules to control physical and logical access to information are established.", "Access Control Policy, access request forms.", ["Access Control"], "CRITICAL"),
    ("Identity management", "🆔", "Verify the full lifecycle of identities (user accounts) is managed.", "Identity management procedure, user list, joiner/leaver records.", ["Access Control"], "CRITICAL"),
    ("Authentication information", "🔑", "Verify allocation and management of authentication information (passwords, keys).", "Password policy, credentials management procedure.", ["Access Control"], "CRITICAL"),
    ("Access rights", "👁️", "Verify that access rights are provisioned, reviewed, and modified.", "User access review reports, access modification logs.", ["Access Control"], "CRITICAL"),
    ("Information security in supplier relationships", "🤝", "Verify processes to mitigate risks associated with supplier access to assets.", "Supplier Security Policy, supplier risk assessments.", ["Software Supply Chain (SBOM)"], "HIGH"),
    ("Addressing information security within supplier agreements", "📝", "Verify that relevant security requirements are established in supplier contracts.", "Supplier contracts/agreements with security clauses.", ["Software Supply Chain (SBOM)"], "HIGH"),
    ("Managing information security in the ICT supply chain", "🚚", "Verify security requirements are defined and monitored down the supply chain.", "Supply chain risk assessment, supplier compliance logs.", ["Software Supply Chain (SBOM)"], "MEDIUM"),
    ("Monitoring, review and change management of supplier services", "📊", "Verify that supplier service delivery is regularly monitored and reviewed.", "Supplier review reports, SLA monitoring logs.", ["Software Supply Chain (SBOM)"], "MEDIUM"),
    ("Information security for use of cloud services", "☁️", "Verify that security requirements for cloud services are established.", "Cloud Security Policy, cloud provider assessments.", ["Software Supply Chain (SBOM)"], "HIGH"),
    ("Information security incident management planning and preparation", "📅", "Verify processes to prepare for and manage security incidents.", "Incident Response Plan (IRP), roles and contact list.", ["Incident Management"], "CRITICAL"),
    ("Assessment and decision on information security events", "⚖️", "Verify that security events are assessed to determine if they are incidents.", "Incident triage logs, classification guidelines.", ["Incident Management"], "HIGH"),
    ("Response to information security incidents", "🚒", "Verify that information security incidents are responded to and managed.", "Incident ticket logs, post-incident reports.", ["Incident Management"], "CRITICAL"),
    ("Learning from information security incidents", "🧠", "Verify that knowledge gained from incidents is used to prevent recurrence.", "Post-Incident Review (PIR) reports, updated procedures.", ["Incident Management"], "MEDIUM"),
    ("Collection of evidence", "🗄️", "Verify that procedures are established for the collection and preservation of evidence.", "Forensics procedure, evidence chain of custody logs.", ["Incident Management"], "MEDIUM"),
    ("Information security during disruption", "🌪️", "Verify information security continuity is planned and implemented during disruption.", "Business Continuity Plan (BCP), emergency response procedure.", ["Business Continuity"], "HIGH"),
    ("ICT readiness for business continuity", "🖥️", "Verify that ICT systems readiness is planned, implemented, and tested.", "Disaster Recovery (DR) Plan, failover testing reports.", ["Business Continuity"], "HIGH"),
    ("Legal, statutory, regulatory and contractual requirements", "⚖️", "Verify that all legal, statutory, regulatory and contractual requirements are identified.", "Compliance register, legal review reports.", ["Risk Assessment"], "HIGH"),
    ("Intellectual property rights", "🔬", "Verify that procedures to protect intellectual property rights are implemented.", "IP protection policy, license compliance checks.", ["Risk Assessment"], "MEDIUM"),
    ("Protection of records", "📂", "Verify that records are protected from loss, destruction, and unauthorized access.", "Records Retention Policy, secure backup configurations.", ["Data Protection & Privacy"], "MEDIUM"),
    ("Privacy and protection of personally identifiable information (PII)", "🔒", "Verify protection of PII according to applicable laws and regulations.", "Privacy Policy, PII inventory, DPA templates.", ["Data Protection & Privacy"], "CRITICAL"),
    ("Independent review of information security", "🔍", "Verify that information security management is independently reviewed.", "Internal audit reports, external audit certificates.", ["Risk Assessment"], "HIGH"),
    ("Compliance with policies and standards for information security", "📏", "Verify regular review of compliance with policies and standards.", "Compliance scans, self-assessment checklists.", ["Risk Assessment"], "HIGH"),
    ("Documented operating procedures", "📚", "Verify that operating procedures for information processing are documented.", "Standard Operating Procedures (SOPs), system runbooks.", ["Risk Assessment"], "MEDIUM")
]

sl = 1
for idx, (name, icon, use_case, expected, scopes, severity) in enumerate(a5_controls, 1):
    code = f"ISO-12{idx:02d}"
    title_name = to_title_case(name)
    controls.append({
        "sl": sl,
        "standard": "ISO 27001",
        "category": "A.5 — Organizational Controls",
        "label": f"{title_name} ({code})",
        "icon": icon,
        "use_case": f"{code} {title_name}",
        "expected": expected,
        "format": "PDF",
        "prompt_hint": f"Verify compliance against {code} {title_name}. {use_case}",
        "scope_tags": scopes,
        "severity": severity,
        "finding": f"No documented evidence found for {code} ({title_name}).",
        "recommendation": f"Establish, document, and implement procedures to satisfy {code} ({title_name})."
    })
    sl += 1

# --- ISO 27001:2022 A.6 (sl 38 to 45) ---
a6_controls = [
    ("Screening", "🔎", "Verify background checks on all candidates for employment are conducted.", "Background check reports, screening policy.", ["Risk Assessment"], "MEDIUM"),
    ("Terms and conditions of employment", "📄", "Verify employment contracts state employee security responsibilities.", "Employment contract templates with security clauses.", ["Risk Assessment"], "MEDIUM"),
    ("Information security awareness, education and training", "🎓", "Verify that employees receive security training and awareness updates.", "Training logs, security awareness presentations.", ["Risk Assessment"], "MEDIUM"),
    ("Disciplinary process", "⚖️", "Verify a formal disciplinary process is established for security breaches.", "Disciplinary Policy, employee handbook.", ["Risk Assessment"], "LOW"),
    ("Responsibilities after termination or change of employment", "🚪", "Verify responsibilities for termination or change of employment remain defined.", "Termination policy, signed exit agreements.", ["Risk Assessment"], "MEDIUM"),
    ("Confidentiality or non-disclosure agreements", "🤫", "Verify that NDAs reflecting security needs are signed by employees and contractors.", "Signed NDA files, NDA template.", ["Risk Assessment"], "HIGH"),
    ("Remote working", "🏠", "Verify security measures are implemented when working remotely.", "Remote Work Policy, VPN logs, MDM setup details.", ["Access Control"], "HIGH"),
    ("Information security event reporting", "📣", "Verify employees are required to report security events promptly.", "Event reporting procedure, report template, ticketing tool screenshots.", ["Incident Management"], "HIGH")
]

for idx, (name, icon, use_case, expected, scopes, severity) in enumerate(a6_controls, 38):
    code = f"ISO-12{idx:02d}"
    title_name = to_title_case(name)
    controls.append({
        "sl": sl,
        "standard": "ISO 27001",
        "category": "A.6 — People Controls",
        "label": f"{title_name} ({code})",
        "icon": icon,
        "use_case": f"{code} {title_name}",
        "expected": expected,
        "format": "PDF",
        "prompt_hint": f"Verify compliance against {code} {title_name}. {use_case}",
        "scope_tags": scopes,
        "severity": severity,
        "finding": f"No documented evidence found for {code} ({title_name}).",
        "recommendation": f"Establish, document, and implement procedures to satisfy {code} ({title_name})."
    })
    sl += 1

# --- ISO 27001:2022 A.7 (sl 46 to 59) ---
a7_controls = [
    ("Physical security perimeters", "🏢", "Verify that physical security perimeters are defined and protected.", "Site map, physical security policy, perimeter control descriptions.", ["Risk Assessment"], "MEDIUM"),
    ("Physical entry", "🚪", "Verify secure physical entry controls protect offices and facilities.", "Access card logs, visitor logbooks, biometric setup.", ["Risk Assessment"], "MEDIUM"),
    ("Securing offices, rooms and facilities", "🔒", "Verify that physical security for offices, rooms, and facilities is designed.", "Office layouts, secure area procedures.", ["Risk Assessment"], "MEDIUM"),
    ("Physical security monitoring", "📹", "Verify that secure facilities are monitored for unauthorized access.", "CCTV records, security guard logs, intrusion alarm test results.", ["Risk Assessment"], "LOW"),
    ("Protecting against physical and environmental threats", "🔥", "Verify protection against natural disasters, fire, and power failures.", "UPS maintenance records, fire suppression inspection, threat assessment.", ["Risk Assessment"], "MEDIUM"),
    ("Working in secure areas", "🛠️", "Verify that rules for working in secure areas are designed and implemented.", "Secure area working rules, visitor access controls.", ["Risk Assessment"], "LOW"),
    ("Clear desk and clear screen", "🖥️", "Verify that clear desk and clear screen rules are defined and enforced.", "Clear Desk / Clear Screen Policy, audit inspection records.", ["Risk Assessment"], "LOW"),
    ("Equipment siting and protection", "🔌", "Verify that equipment is sited and protected to reduce hazards.", "Data center layout, equipment maintenance logs.", ["Risk Assessment"], "LOW"),
    ("Security of assets off-premises", "📦", "Verify security for off-premises assets (laptops, mobile devices).", "Offboarding logs, mobile device security guidelines.", ["Asset Management"], "MEDIUM"),
    ("Storage media", "💾", "Verify storage media is managed through full lifecycle (handling, disposal).", "Media disposal logs, e-waste agreements, media destruction certificates.", ["Asset Management"], "HIGH"),
    ("Supporting utilities", "⚡", "Verify equipment is protected from power failures and utility disruptions.", "Generator test logs, redundant utility SLAs.", ["Risk Assessment"], "LOW"),
    ("Cabling security", "🔌", "Verify power and telecommunications cabling is protected.", "Server room cabling photos, cabling diagrams, security measures description.", ["Risk Assessment"], "LOW"),
    ("Equipment maintenance", "🔧", "Verify equipment is maintained correctly to ensure availability.", "Maintenance schedule, vendor service records.", ["Risk Assessment"], "LOW"),
    ("Secure disposal or re-use of equipment", "♻️", "Verify equipment containing storage media is securely disposed of.", "Decommissioning procedures, data sanitization logs.", ["Asset Management"], "HIGH")
]

for idx, (name, icon, use_case, expected, scopes, severity) in enumerate(a7_controls, 46):
    code = f"ISO-12{idx:02d}"
    title_name = to_title_case(name)
    controls.append({
        "sl": sl,
        "standard": "ISO 27001",
        "category": "A.7 — Physical Controls",
        "label": f"{title_name} ({code})",
        "icon": icon,
        "use_case": f"{code} {title_name}",
        "expected": expected,
        "format": "PDF",
        "prompt_hint": f"Verify compliance against {code} {title_name}. {use_case}",
        "scope_tags": scopes,
        "severity": severity,
        "finding": f"No documented evidence found for {code} ({title_name}).",
        "recommendation": f"Establish, document, and implement procedures to satisfy {code} ({title_name})."
    })
    sl += 1

# --- ISO 27001:2022 A.8 (sl 60 to 93) ---
a8_controls = [
    ("User endpoint devices", "📱", "Verify security controls (encryption, MDM) on endpoint devices.", "MDM policy, disk encryption status reports.", ["Asset Management"], "HIGH"),
    ("Privileged access rights", "⚡", "Verify allocation and use of privileged access rights is restricted.", "Privileged access review, PAM logs.", ["Access Control"], "CRITICAL"),
    ("Information access restriction", "👁️", "Verify access to information is restricted according to access policy.", "Access control list (ACL) reviews, permissions configs.", ["Access Control"], "CRITICAL"),
    ("Access to source code", "💻", "Verify access to source code is restricted to authorized personnel.", "Git repository permission lists, code access policy.", ["Access Control"], "HIGH"),
    ("Secure authentication", "🔑", "Verify secure authentication (MFA, password complexity) is enforced.", "MFA configurations, password policy configuration settings.", ["Access Control"], "CRITICAL"),
    ("Capacity management", "📈", "Verify system resources usage is monitored and tuned.", "Capacity monitoring reports, server resource dashboards.", ["Software Supply Chain (SBOM)"], "LOW"),
    ("Protection against malware", "🛡️", "Verify malware detection and prevention tools are implemented.", "Antivirus deployment logs, EDR config screenshots.", ["Software Supply Chain (SBOM)"], "HIGH"),
    ("Management of technical vulnerabilities", "🔍", "Verify technical vulnerabilities are identified and remediated.", "Vulnerability scanning reports, patch management log.", ["Software Supply Chain (SBOM)"], "HIGH"),
    ("Configuration management", "⚙️", "Verify system configurations (security baselines) are managed.", "Configuration management policy, baseline configs.", ["Software Supply Chain (SBOM)"], "MEDIUM"),
    ("Information deletion", "🗑️", "Verify information is deleted when no longer required.", "Data retention schedule, data deletion records.", ["Asset Management"], "MEDIUM"),
    ("Data masking", "🎭", "Verify data masking is used to protect sensitive data.", "Data masking rules, test database configs.", ["Data Protection & Privacy"], "MEDIUM"),
    ("Data leakage prevention", "🛡️", "Verify DLP measures are implemented for sensitive systems.", "DLP policy, DLP tool logs.", ["Data Protection & Privacy"], "HIGH"),
    ("Information backup", "💾", "Verify backups of information and software are taken and tested.", "Backup logs, backup restoration testing reports.", ["Business Continuity"], "CRITICAL"),
    ("Redundancy of information processing facilities", "🔄", "Verify redundancy is built into information systems.", "High availability config, redundant network paths.", ["Business Continuity"], "HIGH"),
    ("Logging", "📝", "Verify event logs recording user activities, anomalies are produced.", "SIEM config, system logs, log retention policy.", ["Incident Management"], "HIGH"),
    ("Monitoring activities", "📊", "Verify system monitoring is active for anomalous behavior.", "Monitoring system alerts, SOC dashboard logs.", ["Incident Management"], "HIGH"),
    ("Clock synchronization", "⏰", "Verify clocks of all relevant systems are synchronized.", "NTP sync status reports, system clocks config.", ["Incident Management"], "LOW"),
    ("Use of privileged utility programs", "⚡", "Verify utility programs that can override controls are restricted.", "Authorized utility list, utility execution logs.", ["Access Control"], "HIGH"),
    ("Installation of software on operational systems", "📥", "Verify installation of software on production systems is controlled.", "Software installation policy, approved software whitelist.", ["Software Supply Chain (SBOM)"], "MEDIUM"),
    ("Network security", "🌐", "Verify network controls (firewalls, IDS) protect information.", "Firewall rules, network diagrams.", ["Software Supply Chain (SBOM)"], "HIGH"),
    ("Security of network services", "🌐", "Verify security requirements of network services are identified.", "Network service agreements, secure protocol settings.", ["Software Supply Chain (SBOM)"], "MEDIUM"),
    ("Segregation of networks", "🧱", "Verify network groups are segregated based on sensitivity.", "VLAN configurations, network segmentation design.", ["Software Supply Chain (SBOM)"], "HIGH"),
    ("Web filtering", "🌐", "Verify access to external malicious websites is restricted.", "Web filter configs, blocked categories report.", ["Software Supply Chain (SBOM)"], "MEDIUM"),
    ("Use of cryptography", "🔒", "Verify cryptographic controls are designed and implemented.", "Cryptography policy, SSL/TLS settings, encryption key logs.", ["Data Protection & Privacy"], "HIGH"),
    ("Secure development life cycle", "🏗️", "Verify secure development lifecycle (SDLC) rules are established.", "Secure SDLC guidelines, code review guidelines.", ["Software Supply Chain (SBOM)"], "HIGH"),
    ("Application security requirements", "🏗️", "Verify application security specs are defined during design.", "Security requirements documents, threat modeling logs.", ["Software Supply Chain (SBOM)"], "MEDIUM"),
    ("Secure system architecture and engineering principles", "🏛️", "Verify principles for engineering secure systems are followed.", "Architecture design documents, secure engineering guidelines.", ["Software Supply Chain (SBOM)"], "HIGH"),
    ("Secure coding", "💻", "Verify secure coding practices are applied by developers.", "Secure coding guidelines, SAST scan reports.", ["Software Supply Chain (SBOM)"], "HIGH"),
    ("Security testing in development and acceptance", "🧪", "Verify security testing is performed during SDLC.", "Penetration testing report, DAST scans.", ["Software Supply Chain (SBOM)"], "HIGH"),
    ("Outsourced development", "🤝", "Verify outsourced software development is monitored and verified.", "Vendor contracts, code quality reviews for vendor code.", ["Software Supply Chain (SBOM)"], "MEDIUM"),
    ("Separation of development, testing and production environments", "🧱", "Verify dev, test, and production environments are segregated.", "Environment network maps, IAM rules for env separation.", ["Software Supply Chain (SBOM)"], "CRITICAL"),
    ("Change management", "🔄", "Verify changes to systems are controlled, authorized, and logged.", "Change management policy, CAB minutes, change tickets.", ["Software Supply Chain (SBOM)"], "HIGH"),
    ("Test information", "🧪", "Verify test data is selected, protected, and controlled.", "Test data management policy, data sanitization script logs.", ["Software Supply Chain (SBOM)"], "MEDIUM"),
    ("Protection of information systems during audit testing", "🛡️", "Verify audit tests affecting production are planned and approved.", "Audit test schedules, change requests for audit activities.", ["Software Supply Chain (SBOM)"], "LOW")
]

for idx, (name, icon, use_case, expected, scopes, severity) in enumerate(a8_controls, 60):
    code = f"ISO-12{idx:02d}"
    title_name = to_title_case(name)
    controls.append({
        "sl": sl,
        "standard": "ISO 27001",
        "category": "A.8 — Technological Controls",
        "label": f"{title_name} ({code})",
        "icon": icon,
        "use_case": f"{code} {title_name}",
        "expected": expected,
        "format": "PDF",
        "prompt_hint": f"Verify compliance against {code} {title_name}. {use_case}",
        "scope_tags": scopes,
        "severity": severity,
        "finding": f"No documented evidence found for {code} ({title_name}).",
        "recommendation": f"Establish, document, and implement procedures to satisfy {code} ({title_name})."
    })
    sl += 1

# --- DPDP / GDPR Data Protection (sl 94 to 108) ---
dpdp_controls = [
    ("D.1", "Consent collection and management", "CN-201", "📝", "Verify consent is granular, clear, and revocable by the user.", "Privacy notice, consent UI screenshots, consent management records.", ["Data Protection & Privacy"], "CRITICAL"),
    ("D.2", "Privacy notice transparency and readability", "CN-202", "📄", "Verify privacy notice describes purpose and data processing activities clearly.", "Privacy Policy document on website.", ["Data Protection & Privacy"], "HIGH"),
    ("D.3", "Purpose limitation enforcement", "CN-203", "🎯", "Verify data is processed only for purposes explicitly specified.", "Data flow diagrams, processing logs.", ["Data Protection & Privacy"], "HIGH"),
    ("D.4", "Data minimization practices", "CN-204", "📉", "Verify data collection is restricted to what is strictly necessary.", "PII database schema, data minimization guidelines.", ["Data Protection & Privacy"], "MEDIUM"),
    ("D.5", "Data subject rights of access", "CN-205", "👤", "Verify procedures to handle user requests to access their PII.", "DSAR Policy, DSAR response template, access request logs.", ["Data Protection & Privacy"], "HIGH"),
    ("D.6", "Data subject rights of correction and erasure", "CN-206", "🗑️", "Verify procedures to handle user requests to correct or erase PII.", "DSAR Policy, data deletion procedures, deletion execution logs.", ["Data Protection & Privacy"], "HIGH"),
    ("D.7", "Data Protection Officer (DPO) designation", "CN-207", "👔", "Verify designation and public contact availability of DPO.", "DPO appointment letter, CISO/DPO public contact details.", ["Data Protection & Privacy"], "HIGH"),
    ("D.8", "Data breach notification procedures", "CN-208", "🚨", "Verify procedures to notify authorities and users of breach within SLAs.", "Data Breach Policy, incident response log.", ["Data Protection & Privacy"], "CRITICAL"),
    ("D.9", "Cross-border data transfer safeguards", "CN-209", "🌐", "Verify safeguards (SCCs) are in place for cross-border data transfer.", "Standard Contractual Clauses (SCCs), transfer risk assessment.", ["Data Protection & Privacy"], "HIGH"),
    ("D.10", "Data protection impact assessments (DPIA)", "CN-210", "📊", "Verify DPIAs are conducted for high-risk processing activities.", "Completed DPIA reports, DPIA policy.", ["Data Protection & Privacy"], "HIGH"),
    ("D.11", "Privacy by design in development", "CN-211", "🏗️", "Verify privacy considerations are integrated into application design.", "Privacy by design checklist, design review records.", ["Data Protection & Privacy"], "MEDIUM"),
    ("D.12", "Data retention and deletion schedules", "CN-212", "📅", "Verify data is deleted after the retention period expires.", "Data Retention Policy, automated deletion script configs.", ["Data Protection & Privacy"], "HIGH"),
    ("D.13", "Processor agreements and supplier oversight", "CN-213", "🤝", "Verify contracts with third-party processors contain required DP clauses.", "Data Processing Agreements (DPAs) signed with suppliers.", ["Data Protection & Privacy"], "HIGH"),
    ("D.14", "Data security measures (encryption & access control)", "CN-214", "🔒", "Verify encryption and logical controls are implemented for PII database.", "PII database config screenshots, encryption keys management policy.", ["Data Protection & Privacy"], "CRITICAL"),
    ("D.15", "Record of processing activities (ROPA)", "CN-215", "🗄️", "Verify a comprehensive registry of processing activities is maintained.", "ROPA spreadsheet, data processing inventory.", ["Data Protection & Privacy"], "MEDIUM")
]

for orig_code, name, code, icon, use_case, expected, scopes, severity in dpdp_controls:
    title_name = to_title_case(name)
    controls.append({
        "sl": sl,
        "standard": "DPDP / GDPR",
        "category": "DPDP / GDPR Data Protection",
        "label": f"{title_name} ({code})",
        "icon": icon,
        "use_case": f"{code} {title_name}",
        "expected": expected,
        "format": "PDF",
        "prompt_hint": f"Verify compliance against {code} {title_name}. {use_case}",
        "scope_tags": scopes,
        "severity": severity,
        "finding": f"No documented evidence found for {code} ({title_name}).",
        "recommendation": f"Establish, document, and implement procedures to satisfy {code} ({title_name})."
    })
    sl += 1

# --- SOC 2 Trust Services Criteria (sl 109 to 125) ---
soc2_controls = [
    ("S.1", "CC1.1 - Integrity and ethical values", "SOC-301", "🤝", "Verify integrity and ethical behaviors are communicated and monitored.", "Code of Conduct, employee sign-offs, whistleblower policy.", ["Risk Assessment"], "MEDIUM"),
    ("S.2", "CC1.2 - Board oversight and governance", "SOC-302", "👔", "Verify board oversight on controls design and operations.", "Board meeting minutes, governance charter.", ["Risk Assessment"], "MEDIUM"),
    ("S.3", "CC2.1 - Communication of responsibilities", "SOC-303", "📣", "Verify roles and security duties are communicated to employees.", "Employee handbook, security policy acknowledgment logs.", ["Risk Assessment"], "MEDIUM"),
    ("S.4", "CC3.2 - Risk assessment and mitigation", "SOC-304", "📊", "Verify regular risk assessment and mitigation plan is performed.", "Risk assessment matrix, risk mitigation plan.", ["Risk Assessment"], "HIGH"),
    ("S.5", "CC4.1 - Monitoring of controls effectiveness", "SOC-305", "🔬", "Verify regular monitoring of controls effectiveness.", "Internal audit report, compliance dashboard.", ["Risk Assessment"], "HIGH"),
    ("S.6", "CC5.1 - Control activities design and implementation", "SOC-306", "⚙️", "Verify control activities are defined to address risk.", "Risk-control matrix (RCM).", ["Risk Assessment"], "MEDIUM"),
    ("S.7", "CC5.3 - Policy and procedure enforcement", "SOC-307", "📏", "Verify policies and procedures are reviewed annually and enforced.", "Policy review approvals, exception approval logs.", ["Risk Assessment"], "MEDIUM"),
    ("S.8", "CC6.1 - Logical access security and provisioning", "SOC-308", "🔐", "Verify user provisioning and access control is managed.", "Identity management procedure, user provisioning tickets.", ["Access Control"], "CRITICAL"),
    ("S.9", "CC6.2 - User registration and termination", "SOC-309", "🚪", "Verify user termination and revocation of access.", "Offboarding tickets, AD deactivation logs.", ["Access Control"], "CRITICAL"),
    ("S.10", "CC6.3 - Access reviews and modification", "SOC-310", "👁️", "Verify access rights are reviewed periodically.", "User access review reports, manager sign-offs.", ["Access Control"], "CRITICAL"),
    ("S.11", "CC6.6 - Boundary protection (firewalls, WAF)", "SOC-311", "🧱", "Verify firewall rules and external perimeter protections.", "Firewall ruleset export, WAF alerts review logs.", ["Access Control"], "CRITICAL"),
    ("S.12", "CC6.7 - Encryption in transit and at rest", "SOC-312", "🔒", "Verify encryption is used for data at rest and in transit.", "SSL/TLS settings, disk encryption logs, database configs.", ["Data Protection & Privacy"], "CRITICAL"),
    ("S.13", "CC7.1 - Vulnerability management and scanning", "SOC-313", "🔍", "Verify vulnerability scanning and patch management.", "Vulnerability scanning logs, patch reports.", ["Software Supply Chain (SBOM)"], "HIGH"),
    ("S.14", "CC7.2 - Incident detection and logging", "SOC-314", "📝", "Verify system events are logged and audited.", "SIEM log review reports, SOC incident logs.", ["Incident Management"], "HIGH"),
    ("S.15", "CC7.3 - Incident containment and remediation", "SOC-315", "🚒", "Verify incident response plans and actions taken.", "Incident Response Plan, incident ticketing system records.", ["Incident Management"], "CRITICAL"),
    ("S.16", "CC7.5 - Backup restoration and disaster recovery", "SOC-316", "💾", "Verify backups are taken and restoration is tested.", "Backup configs, DR test results, DR runbook.", ["Business Continuity"], "CRITICAL"),
    ("S.17", "CC8.1 - Change management authorization", "SOC-317", "🔄", "Verify change authorizations are required for production release.", "CAB review approvals, CI/CD pipeline code check-in rules.", ["Software Supply Chain (SBOM)"], "HIGH")
]

for orig_code, name, code, icon, use_case, expected, scopes, severity in soc2_controls:
    title_name = to_title_case(name)
    controls.append({
        "sl": sl,
        "standard": "SOC 2",
        "category": "SOC 2 Trust Services Criteria",
        "label": f"{title_name} ({code})",
        "icon": icon,
        "use_case": f"{code} {title_name}",
        "expected": expected,
        "format": "PDF",
        "prompt_hint": f"Verify compliance against {code} {title_name}. {use_case}",
        "scope_tags": scopes,
        "severity": severity,
        "finding": f"No documented evidence found for {code} ({title_name}).",
        "recommendation": f"Establish, document, and implement procedures to satisfy {code} ({title_name})."
    })
    sl += 1

# --- Business Continuity Management (BCMS) (sl 126 to 135) ---
bcms_controls = [
    ("B.1", "Business Impact Analysis (BIA)", "BCP-401", "📊", "Verify BIA is performed to determine RTO/RPO targets.", "BIA report, RTO/RPO definitions document.", ["Risk Assessment"], "HIGH"),
    ("B.2", "Risk assessment for business continuity", "BCP-402", "📊", "Verify risk assessment identifying disruption scenarios.", "Disruption risk assessment report.", ["Risk Assessment"], "HIGH"),
    ("B.3", "Business Continuity Strategy and solutions", "BCP-403", "🗺️", "Verify continuity strategy is approved by management.", "Business Continuity Strategy document.", ["Business Continuity"], "HIGH"),
    ("B.4", "Business Continuity Plans (BCP)", "BCP-404", "📖", "Verify documented BCP is defined.", "Business Continuity Plan (BCP) document.", ["Business Continuity"], "CRITICAL"),
    ("B.5", "Disaster Recovery (DR) Plan", "BCP-405", "🖥️", "Verify documented IT DR plan is defined.", "Disaster Recovery (DR) Plan document.", ["Business Continuity"], "CRITICAL"),
    ("B.6", "Incident response team and communication", "BCP-406", "📞", "Verify incident command structure and emergency communication.", "BCP team contact list, communication templates.", ["Incident Management"], "HIGH"),
    ("B.7", "Testing and exercising (BCP/DR drills)", "BCP-407", "🏃‍♂️", "Verify annual BCP and DR drills are executed.", "BCP test reports, table-top exercise logs.", ["Business Continuity"], "HIGH"),
    ("B.8", "Annual performance evaluation of BCMS", "BCP-408", "📊", "Verify annual review of BCMS effectiveness.", "BCMS performance review report.", ["Business Continuity"], "MEDIUM"),
    ("B.9", "Training and awareness for continuity", "BCP-409", "🎓", "Verify employee training on business continuity roles.", "BCP training presentation, training completion logs.", ["Business Continuity"], "MEDIUM"),
    ("B.10", "Management review and continuous improvement", "BCP-410", "🔄", "Verify annual management review of business continuity.", "Management review meeting minutes, action items list.", ["Business Continuity"], "MEDIUM")
]

for orig_code, name, code, icon, use_case, expected, scopes, severity in bcms_controls:
    title_name = to_title_case(name)
    controls.append({
        "sl": sl,
        "standard": "BCMS (Business Continuity)",
        "category": "Business Continuity Management (BCMS)",
        "label": f"{title_name} ({code})",
        "icon": icon,
        "use_case": f"{code} {title_name}",
        "expected": expected,
        "format": "PDF",
        "prompt_hint": f"Verify compliance against {code} {title_name}. {use_case}",
        "scope_tags": scopes,
        "severity": severity,
        "finding": f"No documented evidence found for {code} ({title_name}).",
        "recommendation": f"Establish, document, and implement procedures to satisfy {code} ({title_name})."
    })
    sl += 1

# --- Software Supply Chain & Licensing (X-BOM) (sl 136 to 142) ---
xbom_controls = [
    ("X.1", "Software inventory and SBOM generation", "XBOM-501", "📋", "Verify that an inventory of software and SBOM is maintained.", "Software inventory list, SBOM files (SPDX, CycloneDX).", ["Asset Management"], "HIGH"),
    ("X.2", "Open source license compliance checks", "XBOM-502", "📄", "Verify checks for open-source licenses usage are performed.", "License scanning reports, open-source policy.", ["Asset Management"], "MEDIUM"),
    ("X.3", "Vulnerability scanning in third-party libraries", "XBOM-503", "🔍", "Verify vulnerability scanning of third-party libraries.", "SCA scan reports (e.g. Snyk, OWASP Dependency-Check).", ["Software Supply Chain (SBOM)"], "HIGH"),
    ("X.4", "Software provenance and signing verification", "XBOM-504", "✍️", "Verify checks on software origin and binary signatures.", "Artifact signing configs, checksum verification logs.", ["Software Supply Chain (SBOM)"], "MEDIUM"),
    ("X.5", "Third-party component end-of-life (EOL) tracking", "XBOM-505", "📅", "Verify monitoring of third-party software end-of-life status.", "EOL software report, upgrade roadmap.", ["Asset Management"], "HIGH"),
    ("X.6", "Supplier security assessment for software vendors", "XBOM-506", "🤝", "Verify software vendors comply with secure development standards.", "Vendor security assessment questionnaires.", ["Risk Assessment"], "MEDIUM"),
    ("X.7", "Secure disposal of media containing software assets", "XBOM-507", "♻️", "Verify secure disposal and sanitization of software media.", "Disposal certificates, media handling procedures.", ["Asset Management"], "HIGH")
]

for orig_code, name, code, icon, use_case, expected, scopes, severity in xbom_controls:
    title_name = to_title_case(name)
    controls.append({
        "sl": sl,
        "standard": "X-BOM (Software Bill of Materials)",
        "category": "Software Supply Chain & Licensing (X-BOM)",
        "label": f"{title_name} ({code})",
        "icon": icon,
        "use_case": f"{code} {title_name}",
        "expected": expected,
        "format": "PDF",
        "prompt_hint": f"Verify compliance against {code} {title_name}. {use_case}",
        "scope_tags": scopes,
        "severity": severity,
        "finding": f"No documented evidence found for {code} ({title_name}).",
        "recommendation": f"Establish, document, and implement procedures to satisfy {code} ({title_name})."
    })
    sl += 1

# Write to file
output = {
    "USE_CASES": controls,
    "DEMO_FINDINGS": {},
    "GAP_RESOLUTION": {}
}

# Create matching DEMO_FINDINGS and GAP_RESOLUTION for each control
for c in controls:
    sl_num = c["sl"]
    ctrl_name = c["use_case"]  # e.g. "ISO-1201 Policies for Information Security"
    
    # We will map standard names or control codes to demo findings
    output["DEMO_FINDINGS"][str(sl_num)] = [{
        "severity": c["severity"],
        "control": ctrl_name,
        "finding": c["finding"],
        "recommendation": c["recommendation"]
    }]
    
    # Simple keyword resolution mapping
    code = ctrl_name.split(" ")[0]  # E.g. "ISO-1201"
    words = [code.lower(), c["label"].lower(), c["use_case"].lower()]
    name_words = c["label"].replace("(", "").replace(")", "").lower().split(" ")
    words.extend([w for w in name_words if len(w) > 3])
    output["GAP_RESOLUTION"][ctrl_name] = list(set(words))

# Add the specific CROSS_FILE findings
output["DEMO_FINDINGS"]["CROSS_FILE"] = [
    {"severity":"CRITICAL","control":"Cross-Document Correlation","finding":"Policy PDF (File 1) mandates 90-day password rotation, but Evidence Certificate (File 2) shows rotation set to 180 days.","recommendation":"Sync the actual system settings with the written policy document."},
    {"severity":"HIGH","control":"Cross-Document Correlation","finding":"Incident Plan (File 1) lists an external vendor for forensics, but the vendor contract (File 2) has been expired for 6 months.","recommendation":"Renew the vendor contract or update the Incident Plan with a new forensic partner."}
]

# Write out python code
with open("controls_data.py", "w", encoding="utf-8") as f:
    f.write("# -*- coding: utf-8 -*-\n")
    f.write("USE_CASES = " + repr(output["USE_CASES"]) + "\n\n")
    f.write("DEMO_FINDINGS = " + repr({int(k) if k.isdigit() else k: v for k, v in output["DEMO_FINDINGS"].items()}) + "\n\n")
    f.write("GAP_RESOLUTION = " + repr(output["GAP_RESOLUTION"]) + "\n\n")
    f.write("""
SCOPE_KEYWORDS = {
    "Access Control": ["access control", "rbac", "mfa", "password", "authentication", "privileged access", "identity management", "pam", "vpn", "credentials", "revoke", "grant access"],
    "Asset Management": ["inventory", "asset list", "acceptable use", "aup", "disposal", "e-waste", "media handling", "sanitization", "laptops", "devices", "return of assets"],
    "Risk Assessment": ["risk assessment", "risk management", "policy", "review", "independent review", "legal requirements", "audit", "compliance", "board oversight", "governance"],
    "Incident Management": ["incident", "breach", "event reporting", "siem", "logging", "monitoring", "containment", "remediation", "triage", "forensics"],
    "Data Protection & Privacy": ["privacy", "pii", "gdpr", "dpdp", "consent", "dpo", "data subject", "dsar", "masking", "dlp", "encryption", "leakage", "retention"],
    "Business Continuity": ["continuity", "disaster recovery", "dr plan", "bcp", "disruption", "redundancy", "backup", "restore", "drill", "rto", "rpo"],
    "Software Supply Chain (SBOM)": ["sbom", "supply chain", "vendor", "supplier", "sdlc", "secure development", "secure coding", "third-party", "libraries", "dependency", "vulnerability scan", "patch"]
}
""")

print("Controls dataset created successfully!")
