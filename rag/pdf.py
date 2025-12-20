# FILE: rag/pdf.py
"""
PDF text extraction and chunking for KEITH Manufacturing Handbook.
The handbook text is embedded directly - no PDF file needed at runtime.
"""

import re
from typing import List, Dict, Optional

# Chunking parameters
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 250

# Embedded handbook text (extracted from TM-Handbook-Updated-01-2025.pdf)
HANDBOOK_PAGES = [
    {"page": 1, "text": "Team Member Handbook\n\nKEITH Manufacturing Co.\nWorld Headquarters\n401 NW Adler St\nMadras, OR 97741\n541-475-3802\n\nRevision Date – January 2025"},
    {"page": 2, "text": """We are thrilled to have you on our team. KEITH Manufacturing Co.'s goal is to bring genuine value, inspiration, and innovation to every KEITH customer, team member, and shareholder. One of our objectives is to provide a work environment that is conducive to both personal and professional growth.

This revised handbook, effective January 1, 2025, is designed to provide you with information about our culture, team member benefits, and some of our guiding principles. Described in the handbook are many of your responsibilities and the programs developed by KEITH Manufacturing Co. This handbook supersedes and replaces any prior versions. If you have questions or concerns, contact HR, Monday through Friday from 6:00 am-4:30 pm.

You can view the handbook online at www.keithwalkingfloor.com/intranet.

It is the sole and absolute discretion of KEITH Manufacturing Co. to revise, supplement, or rescind any policies or portion of the handbook. The only exception to any changes is our employment-at-will policy allowing you or KEITH Manufacturing Co. to end the relationship for any reason, at any time.

As changes occur to the handbook team members will be notified.

Leadership Team
Mark Foster - Chairman/CEO
Lindsay Foster-Drago - Director
Jim Drago - Value Stream Operations Manager
Shane Henning - Value Stream Operations Manager
Mike Feigner - Plant Manager
Eva Johnson - Controller
Alex Ebner - Service Manager
Scott Delamarter - Engineering Manager
Brenda Jones - Human Resources Manager
Laura Crocker - Director of Media
Brian Feigner - Network Admin Manager
James Robinson - Director of Customer Support
Ralph Schukis - Safety Coordinator, Workman's Comp"""},
    {"page": 5, "text": """The KEITH Promise

The continuous pursuit of excellence in KEITH products and customer service.

The evolution of the KEITH® WALKING FLOOR® system began more than half a century ago when Keith Foster first entered the material handling industry by creating specialized agricultural equipment. The WALKING FLOOR® brand was introduced in the 1970s, with interest in the self-unloading system gaining momentum in the 1980s.

Today, KEITH Manufacturing Co. bears little resemblance to the early days. When Keith Foster built his first WALKING FLOOR® system, he had a handful of employees and few resources. The company now encompasses international locations and a global network of dealers. Both mobile and stationary units are used worldwide to move, meter, and unload a variety of products.

Keith built his company around one goal – to produce the most economical, efficient, and safest self-unloading system available. Today, his family carries the tradition forward by introducing innovative products and creative solution to our customers.

"My father was an extraordinary man who defied conventional wisdom and triumphed over seemingly insurmountable obstacles his entire life." ~ Mark Foster, Chairman / CEO"""},
    {"page": 6, "text": """Dear Team Members,

The "One Keith Strategy" focuses our resources and innovation on our markets, to develop the highest quality product, at the lowest possible cost, within the shortest lead time. With respect for people in every step of the process. KEITH utilizes Lean Manufacturing processes throughout our state-of-the-art facility for maximum efficiency. Innovation, R&D, and Continuous Improvement are all focus areas for the company that works toward maintaining a competitive advantage in our industry.

At the core of the One Keith Strategy is High-Performance Team Members. These people share traits that add to their skill and talent to provide innovation and new development within the company. They know what needs to be done, they know how to do it, and most importantly, they get it accomplished. High-Performance Team members display honesty & courage, accountability & care, gratitude & loyalty, fairness & humility, and patience & presence. Our values include being a Team Member with Integrity, a Positive Attitude, and being a Problem Solver.

The One Keith Strategy is the roadmap for achieving our goals in creating a lasting mutually beneficial relationship with customers, vendors, and team members. There are many ways to get there; most importantly, you become part of the journey.

Chairman/CEO

One TEAM ~ One PLAN ~ One GOAL ~ One KEITH"""},
    {"page": 7, "text": """Nature of Employment

Employment with KEITH Manufacturing Co. is voluntary, and the team member is free to resign at will at any time, with or without cause. Similarly, KEITH Manufacturing Co. may terminate the employment relationship at will at any time, with or without notice or cause, so long as there is no violation of applicable federal or state law.

Policies outlined in this handbook are not intended to create a contract, nor are they to be construed to constitute contractual obligations of any kind or a contract of employment between KEITH Manufacturing Co. and any of its team members. The provisions of the handbook are at the discretion of leadership and, except for its policy of employment-at-will, may be amended or canceled at any time, at KEITH Manufacturing Co.'s sole discretion.

Equal Employment Opportunity/No-Discrimination Policy

KEITH Manufacturing Co. provides equal opportunity to all qualified team members and applicants without unlawful regard to race, color, religion, gender, sexual orientation, national origin, age, disability, genetic information, marital status, or any other status protected by applicable federal, state, or local law. This policy applies to all aspects of the employment relationship – including but not limited to, recruitment, hiring, compensation, promotion, demotion, transfer, disciplinary action, layoff, recall, and termination of employment.

KEITH Manufacturing Co. is committed to complying fully with all disability discrimination laws. The company will provide reasonable accommodations for qualified individuals with known disabilities unless doing so would result in an undue hardship.

Immigration Law Compliance

KEITH Manufacturing Co. is committed to employing only United States citizens and those who are authorized to work in the United States. In compliance with the Immigration Reform and Control Act of 1986, each team member, as a condition of employment, must complete the Employment Eligibility Verification form I-9 and present documentation establishing identity and employment eligibility.

Personnel Data Changes

It is the responsibility of each team member to notify KEITH Manufacturing Co. of any changes in personnel data (personal mailing addresses, telephone numbers, number and names of dependents, and individuals to be contacted in the event of an emergency). Team Members may update their personal information through Paycom or by notifying Human Resources. Team members may not use the company address for personal mail."""},
    {"page": 8, "text": """Employment Agreements: Non-Disclosure/Non-Compete

The protection of confidential business information and trade secrets is vital to the interests and the success of KEITH Manufacturing Co. Such Confidential information includes but is not limited to: Compensation Data, Pending projects and proposals, Customer Information, Proprietary production processes, Research and development strategies, Customer preferences, Financial information, Scientific data, Labor relations strategies, Scientific formulae, Marketing strategies, Scientific prototypes, New materials research, Technological data.

All team members may be required to sign a non-disclosure agreement as a condition of employment. Any team member who improperly uses or discloses trade secrets or confidential business information will be subject to disciplinary action, up to and including termination of employment and legal action.

Any team member who has another job or business of their own must notify KEITH Manufacturing Co. at the time of hire, or as soon as the business is formed. Any team member needs to have approval in writing from the CEO or Leadership Team to perform the duties of a second job.

Employment Categories

Onboarding: Team members currently being evaluated to determine whether continued employment is appropriate. The onboarding period is 90 days unless the team leader and group leader deem an extension of time necessary. A significant absence will automatically extend an onboarding period.

Regular full-time: Team members not in an onboarding period who are regularly scheduled to work 40 hours per week. Regular full-time team members are eligible for the company benefits package. Health Insurance Benefits require team members to work a minimum of 30 hours each week.

Non-Exempt/Exempt: All team members are defined as either "Non-Exempt" or "Exempt" in accordance with the Fair Labor Standards Act, which determines whether the team member is eligible for overtime. Most positions at KEITH Manufacturing Co. are Non-Exempt.

Rest & Meal Periods

KEITH Manufacturing Co. provides meal and rest periods to team members. Meal periods and rest breaks are mandatory. Non-exempt team members are required to take at least a 30-minute unpaid meal period when the work period is six hours or greater. Team members must clock-out before leaving the company premises."""},
    {"page": 9, "text": """Break & Meal Alert System

The company has a speaker system throughout production areas to notify team members of break or meal period rest time. A single whistle will blow at the beginning of each break. A 2-minute warning whistle will blow toward the end of the break as a signal to head back to the work area.

Overtime

When operating requirements or other needs cannot be met during regular working hours, team members may be required to work overtime. All overtime work must receive the team leader and group leader/manager's prior authorization. Overtime compensation is paid to all nonexempt team members following federal and state wage and hour restrictions. Overtime pay is based on actual hours worked. Time-off due to illness, vacation, holiday, or any leave of absence will not be considered hours worked for purposes of performing overtime calculations. Overtime is never guaranteed.

Paydays & Work Week

All team members are paid biweekly on every other Friday. The workweek is Monday-Sunday. Direct Deposit is available to all eligible team members and is encouraged. Paychecks are available for pick up on the Thursday before payday in the main office from 3:30pm – 4:30pm. Team members may access their paystubs online through Paychex.

Pay Corrections & Payroll Maintenance Changes

KEITH Manufacturing Co. takes all reasonable steps to ensure that team members receive the correct amount of pay in each paycheck. In the unlikely event that there is an error of pay, the team member should promptly bring the discrepancy to the attention of Human Resources or Payroll. Payroll changes need to be submitted by Thursday of the week before payday.

Payroll Advance

Team members can request a payroll advance any time through Payactiv. Please contact HR for more information.

Performance Evaluation

Leaders and team members are strongly encouraged to discuss job performance and goals on an informal, day-to-day basis. Annual evaluations are conducted to provide both leaders and team members the opportunity to discuss job tasks, attendance, and identify strengths and opportunities.

Team Member Termination

RESIGNATION – voluntary employment termination initiated by a team member.
DISCHARGE – involuntary employment termination initiated by the organization.

Since employment with KEITH Manufacturing Co. is based on mutual consent, both the team member and KEITH Manufacturing Co. have the right to terminate employment at will, with or without cause, at any time."""},
    {"page": 10, "text": """TIME-OFF PROGRAM

KEITH Manufacturing Co.'s Time-off Program, including Paid Vacation Time, Paid Sick Time, and Personal Unpaid Time, allows you to take time off from work for your family and personal needs.

Effective use of your time off is a personal responsibility, and we expect that you will be conscientious of your attendance and punctuality at work. The success of your team depends on the contributions of each team member. Regular and dependable attendance is an essential function of your job.

Scheduled Absences
Scheduled absences are those for which you obtain pre-approval during business hours from your group leader/manager.

Vacation Pay
To be eligible, you must be a full-time KEITH Team Member and have successfully completed your 90-day On-Boarding period. You may use your Vacation Pay as a paid day off or a 'Pay Only'. However, if using your Vacation Pay as a Pay Only, you cannot save your vacation "time" for a later date. The time piece is attached to Vacation Pay.

The accrual level is based on years of service:

On-Boarding (after 90 days) through 4th year:
- Vacation Pay: 3.08 hrs. per pay period = 80 hrs. per year
- Sick Pay: Up to 40 hours per year. 1 hour of sick time is accrued for every 30 hours worked.
- Personal Unpaid Time: 80 hours frontloaded per calendar year (40 hours if hired after June 30th)

Beginning of 5th year through end of 9th year:
- Vacation Pay: 3.70 hrs. per pay period = 96 hrs. per year
- Sick Pay: Up to 40 hours per year
- Personal Unpaid Time: 80 hours frontloaded per calendar year

Beginning of 10th year through end of 19th year:
- Vacation Pay: 4.62 hrs. per pay period = 120 hrs. per year
- Sick Pay: Up to 40 hours per year
- Personal Unpaid Time: 80 hours frontloaded per calendar year"""},
    {"page": 11, "text": """Beginning of 20th year:
- Vacation Pay: 6.16 hrs. per pay period = 160 hrs. per year
- Sick Pay: Up to 40 hours per year
- Personal Unpaid Time: 80 hours frontloaded per calendar year

If you are unable to arrive as scheduled, before the start of your shift call – (541)475-3802 press #8 on your phone keypad and leave a voicemail. (If reception answers ask for the "employee call in line")

TM's that exhaust all time-off hours may be subject to disciplinary actions. Team members that exhibit repeated patterns of unacceptable attendance should expect more severe discipline.

Paid hours accrued will be paid:
- During the pay period in which you request Vacation Pay.
- When hourly non-exempt team members exceed 150% of accrued Vacation Pay, the accrual will stop until more pay is used.
- Vacation Pay will be paid out for hourly non-exempt team members upon termination if 90 days of employment are completed.

VACATION PAY CAP: When hourly non-exempt team members exceed 150% of accrued Vacation Pay, the accrual will stop until more pay is used.

Sick Pay (Oregon Sick Leave Act)
Team members accrue 1 hour of Sick Pay for every 30 hours worked and the accrual will stop at 40 hours for the year. Unused Sick Pay will not get paid out and will reset for accrual at the beginning of the next calendar year. Unused Sick Pay will not be paid out upon separation of employment.

Personal Unpaid Time
Team members will be frontloaded 80 hours of Personal Unpaid Time every calendar year. New hires starting after June 30th will be frontloaded with 40 hours of Personal Unpaid Time. Unused hours will not carry over to the next calendar year.

Requesting Time-off
Before taking time off, submit a Time-Off Request form electronically to your GL/Manager. Requests may be sent from your desktop, through your Paychex app or a kiosk. Time-Off requests are to be submitted during break/lunch periods. You may request Time-off in one-hour increments."""},
    {"page": 12, "text": """Punctuality and Tardiness

To create a safe and consistent work atmosphere, all TMs are expected to be punctual and prepared to start their shift at their scheduled time. If you are late for work, you place a burden on your team, and this may cause production and customer care to suffer.

Team members are required to clock out when leaving the premises for lunch or other events.

A tardy arrival is any time a team member arrives after the scheduled shift start time or returning from a lunch period or punching out before the end of the shift time.

Arrival for scheduled shift, 16 or more minutes late, will incur both a tardy and 1-hour reduction of Personal Unpaid Leave. If Personal Unpaid Leave has been exhausted, then Vacation Pay will be deducted.

Tardy Policy:
- More than four tardies within six months (January-June and July-December) will result in disciplinary action
- Tardy #5 will result in a one-day suspension
- Tardy #6 will result in a 20% loss of bonus for performance and a one-day suspension
- Repeated patterns of tardies may result in more than one day of suspension

Excessive Absences and Tardiness
A second suspension will include 20% loss of the next payout of bonus for performance. A third suspension will include 40% loss. A fourth suspension will include 60% loss. Bonus for performance is based on fiscal year (July 1 – June 30).

Job Abandonment
Team Members that are no show/no call for one workday without calling in is considered to have voluntarily terminated their employment.

If Your Employment Ends
Unused Paid Time-off Hours will be paid on the final paycheck for hourly non-exempt team members that have completed their 90-day introductory period. Salaried exempt team members will not be paid out unused vacation pay.

Jury Duty
KEITH Manufacturing Co. does not pay team members for jury time. Team members should submit a copy of the jury summons to HR.

Holiday Pay
KEITH Manufacturing Co. team members are eligible for six (6) paid holidays per year:
- New Years' Day
- Memorial Day
- Fourth of July
- Labor Day
- Thanksgiving Day
- Christmas Day

To be eligible: Be on payroll, work the fully scheduled shift both the day before and the day after the holiday unless pre-approved. Holiday time is not considered time worked for overtime calculation."""},
    {"page": 13, "text": """Leave of Absences

KEITH Manufacturing Co. provides medical leaves of absence to eligible team members who are temporarily unable to work due to a serious health condition or disability.

FMLA – Federal Medical Leave Act
KEITH Manufacturing Co. team members may be eligible for up to 12 weeks per year of unpaid job protected leave.

To be eligible for FMLA:
- Must have worked for a covered employer for at least 12 months
- Must have worked at least 1,250 hours during the 12-month period immediately preceding the leave

FMLA provides up to 12 weeks of leave in a 12-month period for:
- The birth, adoption or foster placement of a child with you
- Your own serious mental or physical health condition that makes you unable to work
- To care for your spouse, child or parent with a serious mental or physical health condition
- Certain qualifying reasons related to the foreign deployment of your spouse, child or parent who is a military servicemember

Definition of a family member under FMLA:
- A spouse (includes individual in a common law marriage)
- Parent (biological, adoptive, step or foster father or mother)
- Child (biological, adopted, foster or stepchild) who is either under age 18, or older and "incapable of self-care because of a mental or physical disability"

OFLA Oregon Family Leave Act
To be eligible for OFLA, a team member must have worked an average of 25 hours per week for 180 days.

OFLA provides up to 12 weeks of time off per year for:
- Providing care for your child related to an illness, injury or conditions that requires home care
- Bereavement – up to two weeks for the death of an individual related by blood or affinity
- Pregnancy disability leave - up to 12 additional weeks for pregnancy disability
- Military family leave up to 14 days

Definition of family member under OFLA extends to grandparents, grandchildren, parents-in-law, same-gender domestic partners, siblings, and any individual related by blood or affinity whose close association is equivalent to a family relationship.

If leave falls under FMLA and/or OFLA, leave will run concurrently. Keith Manufacturing will follow whichever is more beneficial to the employee."""},
    {"page": 14, "text": """Covered Conditions for FMLA/OFLA – Threshold requirement: unable to perform at least one essential function of job

- In-patient care & recovery
- Pregnancy, prenatal care
- Terminal Illness
- Continuing Treatment (includes diagnosis)

Incapacity (inability to work) of more than three consecutive calendar days that also involves:
- Two or more treatments by health care provider within 30 days of incapacity, or
- One treatment and continuing supervision (includes prescription medications and equipment)

Chronic Serious Health Conditions:
- Periodic treatment by the health care provider
- Continue over an extended period
- May be episodic (Asthma, diabetes, epilepsy)

Permanent or long-term period of incapacity (Alzheimer's, Stroke)

Multiple treatments for:
- Restorative surgery for accident or another injury
- Cancer-chemotherapy or radiation
- Arthritis-physical therapy
- Kidney dialysis

Explicitly NOT covered under FMLA rules: Colds, Flu, Earaches, Upset Stomach, Minor Ulcers, Headache (except migraine), Routine eye or dental treatment.

Team members should make requests for medical leave at least 30 days in advance of foreseeable events.

Paid Leave Oregon

Paid Leave Oregon is administered by the Oregon Employment Department. This program allows individuals to take up to 12 weeks of paid time off from work in a year. Employers pay 40% of the 1% contribution rate, and employees pay 60%.

You can take leave for a week or a single day at a time.

Paid leave protects an employee's job and role if they've worked for the same employer for at least 90 consecutive days.

Eligibility Requirements:
- Currently work in Oregon
- Made at least $1,000 in Oregon in their base year before applying"""},
    {"page": 15, "text": """Qualifying life events for Paid Leave Oregon:
- Caring for and bonding with a child in the first year after birth or placement through adoption/foster care
- Completing necessary activities before adopting a child or having a foster care child join your home
- To care for a family member with a serious illness or injury
- To care for yourself when you have a serious illness or injury
- You or your child are a survivor of sexual assault, domestic violence, harassment, bias crimes, or stalking

A "family member" under Paid Leave Oregon includes:
- Spouse or domestic partner
- Child (biological, adopted, stepchild, or foster child)
- Parent (biological, adoptive, stepparent, foster parent, or legal guardian)
- Sibling or stepsibling
- Grandparent or grandchild
- Any person you are connected to like a family member

30-day notice: If you know you will need to take Paid Leave, you need to let your employer know 30 days before taking leave.

Unexpected leave: You must tell your employer within 24 hours of starting your leave. You must give written notice within 3 days after starting leave. If you don't give written notice, your first weekly benefit payment may be reduced by 25%.

Any leave taken through Paid Leave Oregon that also qualifies under FMLA and/or OFLA will run concurrently.

For all medical leave of absences: A health care provider's statement is required verifying the need for medical leave and its beginning and expected end dates. Team members returning from medical leave must submit a health care provider's verification of their fitness to return to work.

Benefits

Eligible team members are provided with a wide range of benefits including Social Security, workers' compensation, state disability, and unemployment insurance.

Medical, Dental, Pharmacy, Vision, Term Life Insurance
The health benefits program is available to eligible team members on the first day of the month following 60 days of continuous employment.

Vacation, Sick Pay, 401(K)
Paid Time-off is available to new team members on the 91st day of employment.

Flexible Savings Account Enrollment is annually for the January 1st renewal."""},
    {"page": 16, "text": """Policies & Procedures

KEITH Manufacturing Co. is committed to maintaining a workplace environment that promotes and protects the safety and health of all customers, team members, vendors, and visitors.

Anti-Harassment Policy

KEITH Manufacturing Co. will not tolerate unlawful discrimination or harassment of any kind. Based on the seriousness of the offense, disciplinary action may include coaching, verbal and written reprimand, suspension, or termination of employment.

Forms of prohibited harassment under Federal and Oregon law include harassment based on race, color, religion, national origin, age, sexual orientation, marital status, disability, protected activity, and any other status protected by law.

KEITH Manufacturing Co. prohibits team members from engaging in any conduct that is disrespectful, insubordinate, or that creates a hostile work environment:
- Verbal: slandering, ridiculing, or insulting a person; persistent name-calling; abusive remarks
- Physical: pushing, shoving, kicking, poking, tripping, assault, threat of physical attack
- Gesture: non-verbal threatening gestures
- Exclusion: socially or physically excluding or disregarding a person in work-related activities

Anti-Workplace Bullying Policy

Workplace Bullying is repeated inappropriate behavior, either direct or indirect, whether verbal, physical or otherwise. When an allegation of bullying is made, the intention of the alleged bully is irrelevant. It is the effect of the behavior on the individual that is important.

Conduct that may constitute bullying includes: singling out of one person, shouting at an individual, ignoring or interrupting, personal insults, use of offensive nicknames, constant criticism, spreading rumors, deliberately excluding a person, public humiliation, interfering with another person's work, taking credit for another person's ideas.

Definitions:
- Unlawful Discrimination: Different treatment based on protected status
- Workplace Bullying: A persistent pattern of mistreatment causing physical or emotional harm
- Harassment: Unwelcome conduct based on protected status that interferes with employment
- Sexual Harassment: Unwelcome sexual conduct creating a hostile environment or used as basis for employment decisions
- Retaliation: Adverse treatment for engaging in protected activity"""},
    {"page": 17, "text": """Resolution Procedure for Harassment/Discrimination

If you believe that you have experienced any harassment or discrimination, you are expected and required to bring the matter to the attention of your team leader, group leader or Human Resources as soon as possible.

If you believe it would be inappropriate to discuss the matter with your team leader or group leader, go directly to Human Resources. A meeting with the Chairman/CEO is always an option.

Any team member who observes conduct that constitutes harassment or discrimination must immediately report the matter to a team leader, group leader, or Human Resources.

All complaints and reports will be promptly and impartially investigated and will be kept confidential to the extent possible. Any team member found to have violated this policy will be subject to disciplinary action, up to and including termination of employment.

Procedure:
1. Address the problem with your team leader as soon as possible
2. If not satisfactory, request a meeting with your group leader/manager
3. If still not resolved, request a meeting with your group leader/manager and the Human Resources Manager
4. If a problem involves a member of leadership, you may omit that step and proceed to the next

Protection Against Retaliation

KEITH Manufacturing Company prohibits retaliation against any team member who has made a good-faith complaint, has reported harassing or discriminatory conduct, or has participated in an investigation. Any team member found to have retaliated will be subject to disciplinary action up to and including termination.

Team members that file groundless, malicious, or anonymous claims will be considered abusing this policy and will be treated as a policy violation.

Defend Trade Secrets Act: An individual shall not be held liable for disclosure of a trade secret made in confidence to a government official or attorney solely for reporting or investigating a suspected violation of law."""},
    {"page": 18, "text": """Weapons
Any unauthorized possession or inappropriate use of firearms or weapons on KEITH Manufacturing Co.'s property, or while on KEITH Manufacturing Co. business is prohibited.

Mischievous Pranks
Pranks and horseplay will not be tolerated and is grounds for discipline up to and including termination of employment.

Smoking
Smoking in the workplace is prohibited except in designated smoking areas.
- Do not light your cigarette on the way to the designated area
- Use provided containers for cigarette butts – not the ground or floor
- Violation will result in immediate disciplinary action up to and including termination

Parking
Parking is available in the paved parking lot and across the streets on a first-come basis. Designated areas are marked reserved.

Use of KEITH Manufacturing Co. Equipment and Vehicles
Team members are expected to exercise care, perform required maintenance, and follow all operating instructions, safety standards, and guidelines. The interior of a vehicle is expected to be clean when returned.

Please notify your group leader/manager if any equipment, machine, tools, or vehicles appear to be damaged, defective, or in need of repair.

Driving Policy
KEITH Manufacturing Co. has a zero-tolerance policy regarding using a cell phone while driving, except under conditions allowed by law.
- Keep both hands on the wheel while driving
- Pull over in a legal and safe location to use electronic devices
- Allow voicemail or passengers to take calls while driving

Cell Phone Policy
While at work, team members are expected to exercise discretion in using cellular phones. Team members are encouraged to make personal calls or send text messages during breaks and lunch. KEITH Manufacturing Co. is not liable for loss or damage of personal cell phones.

Audio Headphones/Earbuds in the Workplace:
- If situational awareness is compromised (can't hear emergency alarms), devices must not be used
- High volumes can cause permanent hearing loss
- Team members are expected to use a single earpiece to maintain awareness"""},
    {"page": 19, "text": """Cameras on Phones
KEITH Manufacturing Co. prohibits the recording or sharing of images on company property without consent from a member of the Leadership team.

KEITH Manufacturing Co. Provided Phones & Devices
Some team members may be issued a company cell phone for their job functions. Team members are always required to be professional and conscientious when using company phones.

Responsibilities:
- Protect equipment from loss, damage, or theft
- Coordinate international travel requirements with the Cell Phone Coordinator before leaving the US
- Failure to coordinate international plan updates creates significant expense for the company

Usage and Fees:
- Phones are issued primarily for business use
- Make every effort not to exceed contracted allowed minutes
- Fee-based mobile applications require group leader/manager approval
- Additional costs apply for voice and data when traveling internationally
- Excessive fees related to unauthorized or personal usage will be the team member's responsibility

Termination of Employment
The cell phone and cell phone number are the property of KEITH Manufacturing Co. If the team member leaves the company, the property must be returned immediately before the last day worked."""},
    {"page": 20, "text": """Computer Related User Policy

KEITH Manufacturing Co. has established a policy with regards to computer systems. All existing company policies apply to conduct on KEITH Manufacturing Co. computer systems.

Email Signature Guidelines:
- Type: Arial
- Size: 12 pt.
- Color: Black & Blue
- Background: White
- Confidential statement: Arial, 10 pt. & Black

Policy:
- USERS must use Internet and email appropriately and consistent with the Code of Conduct and Ethics
- USERS must avoid sites that could bring KEITH MANUFACTURING CO. into disrepute
- USERS must not use personal email accounts for business purposes
- USERS may use Internet and email for personal purposes during break time and lunchtime, provided it doesn't detract from work performance
- USERS must observe intellectual property rights (copyright, patent, trademark, license agreements)
- USERS are responsible for actions taken under their assigned user account
- USERS are responsible for safeguarding email accounts and passwords
- USERS must not read another team member's email except as directed by a group leader/manager
- USERS must not use bcc: without group leader/manager permission
- USERS must not express personal views in public forums (chat rooms) without permission
- USERS must not mask or falsify their identity online
- USERS will not print personal emails or Internet information without payment and permission

KEITH MANUFACTURING CO. reserves the right to monitor and investigate individual users' Internet or email activity.

Inappropriate use may lead to restricted access or disciplinary action up to and including dismissal."""},
    {"page": 21, "text": """Drug & Alcohol Policy - KEITH Manufacturing Co. is a Drug-Free Workplace

KEITH Manufacturing Co. recognizes a responsibility to maintain a safe and productive work environment. Team members are required to report to work in appropriate mental and physical condition.

Policy Provisions:
- All team members are expected to report fit for duty without limitations due to alcohol, illicit drugs, non-prescription drugs, or prescribed medication
- KEITH Manufacturing Co. has zero-tolerance for team members who arrive under the influence of alcohol or drugs
- Strictly prohibits the use, making, sale, purchase, transfer, distribution, consumption, or possession of drugs or alcohol on company property
- If taking potentially impairing medication at work, notify Human Resources before your shift
- An illegal drug or alcohol violation must be reported to HR within five calendar days

Drug Testing occurs:
- Pre-Employment
- Reasonable suspicion
- Involvement in a safety incident or accident

Actions following a Positive Drug/Alcohol Test:
Any team member whose test yields a presumptive positive will be automatically suspended pending confirmation. Overall work history, attendance, and circumstances will determine continued employment status.

Continued employment is not promised, guaranteed, or implied following a violation.

Safety

The active interest and cooperation of each team member is vital to the success of our safety program. Safety is the responsibility of everyone.

Each team member receives a complete Safety Handbook at the time of hire. Additional copies are available in Human Resources and with the Safety Coordinator."""},
    {"page": 22, "text": """Team member responsibilities for safety:
1. Safety glasses – must always be worn in designated areas marked "Caution Eye Protection Required." Exceptions must be approved in writing by a Group Leader and the Safety Coordinator.
2. Report unsafe conditions and practices to leaders as soon as possible
3. Conduct work activities in a manner that will not endanger others
4. Set an example for new team members
5. Undertake only those jobs you are authorized to do and understand
6. Make safety suggestions
7. Report all injuries to your leader immediately with a written report to the Safety Coordinator
8. Report accidents or property damage to team leader immediately

Safety Meetings
Group Leaders or Managers will include safety items and potential hazards as a regular part of value stream meetings. This includes discussion of recent injuries and solutions to prevent future accidents.

Dress Code
Office attire is casual, jeans and t-shirts are acceptable. Items with offensive words, terms, or pictures should not be worn. Clothing revealing excessive skin (cleavage, chest, back, shoulders, stomach) is unacceptable. Skirts or dresses must be business appropriate length. Shorts and open-toed shoes are not allowed in any production area.

Travel Time
On overnight trips, all time spent traveling will be compensated, including weekends. While traveling, time should be spent preparing service reports, expense reports, etc. Team members should have all reports completed before returning to work when possible.

Time reporting for the workweek is Monday – Sunday. No later than Monday morning by 7:00 am (PST) team members must email Payroll all time for the previous week.

Referral Program
If a candidate you refer is hired and completes six months of employment, KEITH Manufacturing Co. will include $750 in your paycheck. Candidates must list the KEITH team member in the "Referred By" box on their application. Team members are not eligible for $750 for referring a returning team member.

Plant Visitor Rules
No one is allowed in plant facilities unless:
- A team member on their scheduled shift
- A vendor accompanied by a team member or signed the visitor log
- A customer accompanied by a team member"""},
    {"page": 23, "text": """Internal Transfers

KEITH Manufacturing Co. is dedicated to building an inspiring place to work where all team members strive to be the best they can be. As a company, we emphasize team building through promotion within and team member engagement.

Procedure for Filling Open Positions:
- Group Leader/Manager receives approval from Mark Foster to fill an open position
- Manager/Group Leader submit an Open Position Approval form to HR
- Internal Job Post will be distributed to company email, communication board, Work Source Oregon, and other job posting sites
- Applications accepted in HR Office before or after scheduled work hours, lunch, or scheduled breaks
- Leadership may, at any time fill a position that is in the best interest of KMC

Guidelines for Internal Candidates:
- Preference given to KEITH Team Members employed for at least six months
- Must meet qualifications listed for the position
- Complete an Internal Application (available in HR Office)
- Obtain current Team Leader and Group Leader initials on application
- Team Member may not apply for two positions at the same time
- Must be in good standing in terms of overall work performance and attendance
- Submit applications to the HR Office
- Team member may not move to a new position until a replacement is trained"""},
    {"page": 24, "text": """KEITH COMPANY GOALS:

Customer first service / promise of highest quality / superior value / continuous innovation / lowest total cost of ownership

KEITH MANUFACTURING CO
401 NW Adler St
Madras, OR 97741"""}
]


def extract_section_title(text: str) -> Optional[str]:
    """Extract section title from chunk text."""
    lines = text.strip().split('\n')
    for line in lines[:3]:
        line = line.strip()
        if line and len(line) < 100:
            if line.isupper() or line.endswith(':'):
                return line.rstrip(':')
            if any(keyword in line.lower() for keyword in 
                   ['policy', 'procedure', 'section', 'leave', 'benefits', 
                    'time-off', 'safety', 'code', 'rules', 'program',
                    'employment', 'vacation', 'sick', 'holiday', 'fmla', 'ofla']):
                return line
    return None


def chunk_text(
    text: str,
    page_number: int,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP
) -> List[Dict]:
    """Split text into overlapping chunks."""
    if not text or len(text) < 50:
        return []
    
    chunks = []
    paragraphs = text.split('\n\n')
    current_chunk = ""
    chunk_index = 0
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        
        if len(current_chunk) + len(para) > chunk_size and current_chunk:
            section_title = extract_section_title(current_chunk)
            chunks.append({
                "chunk_id": f"p{page_number}_c{chunk_index}",
                "text": current_chunk.strip(),
                "page_number": page_number,
                "section_title": section_title or f"Page {page_number}"
            })
            chunk_index += 1
            
            # Keep overlap
            words = current_chunk.split()
            overlap_words = words[-(chunk_overlap // 6):] if len(words) > chunk_overlap // 6 else []
            current_chunk = ' '.join(overlap_words) + '\n\n' + para
        else:
            current_chunk += '\n\n' + para if current_chunk else para
    
    # Don't forget the last chunk
    if current_chunk.strip():
        section_title = extract_section_title(current_chunk)
        chunks.append({
            "chunk_id": f"p{page_number}_c{chunk_index}",
            "text": current_chunk.strip(),
            "page_number": page_number,
            "section_title": section_title or f"Page {page_number}"
        })
    
    return chunks


def extract_pdf_chunks() -> List[Dict]:
    """
    Extract and chunk all text from the embedded handbook.
    No PDF file needed - uses embedded text.
    """
    all_chunks = []
    global_chunk_id = 0
    
    for page_data in HANDBOOK_PAGES:
        page_num = page_data["page"]
        text = page_data["text"]
        
        page_chunks = chunk_text(text, page_num)
        
        for chunk in page_chunks:
            chunk["chunk_id"] = f"chunk_{global_chunk_id}"
            global_chunk_id += 1
            all_chunks.append(chunk)
    
    return all_chunks
