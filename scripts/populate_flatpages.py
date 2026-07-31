import os
import django
import sys

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pythonweekend.settings")
django.setup()

from django.contrib.flatpages.models import FlatPage
from django.contrib.sites.models import Site

def create_or_update_flatpage(url, title, content):
    site, _ = Site.objects.get_or_create(id=1, defaults={"domain": "example.com", "name": "example.com"})
    
    page, created = FlatPage.objects.get_or_create(
        url=url,
        defaults={"title": title, "content": content}
    )
    
    if not created:
        page.title = title
        page.content = content
        page.save()
        
    page.sites.add(site)
    print(f"[{'Created' if created else 'Updated'}] {title} ({url})")

def run():
    pages = [
        (
            "/support-us/",
            "Support a Workshop",
            """<h1>Support a Workshop Page</h1>
<h2>Why Support Python Weekend?</h2>
<h3>Our Mission</h3>
<p>Python Weekend helps complete beginners learn Python and take their first practical step into artificial intelligence through free, mentor supported workshops.</p>
<p>We support local volunteer teams with a shared programme framework, organiser guidance, learning resources and central coordination. Partners make it possible for these teams to provide the spaces, tools and participant support required for a strong learning experience.</p>
<p>Our goal is to make Python and AI education more accessible, especially for people who have had limited opportunities to enter technology.</p>
<p>We are committed to being transparent about the workshops and activities supported by our partners. Verified outcomes should be published in periodic impact reports.</p>
<h2>Start Supporting Python Weekend Today</h2>
<h3>Sponsor a Local Workshop</h3>
<p>Support a specific Python Weekend edition by contacting its local organising team. Local sponsorship may cover venue costs, internet access, participant meals, learning materials, transport support, photography or equipment.</p>
<a href="/events/" class="btn">View upcoming events</a>
<h3>Become a Programme Partner</h3>
<p>Companies and institutions can support several Python Weekend editions or contribute to resources used across the community.</p>
<p>Programme partnerships may support curriculum development, organiser training, mentor preparation, website infrastructure, accessibility or the expansion of Python Weekend into new cities.</p>
<a href="/contact/" class="btn">Discuss a partnership</a>
<h3>Provide In Kind Support</h3>
<p>Partners may provide:</p>
<ul>
<li>Learning venues</li>
<li>Laptops and devices</li>
<li>Internet connectivity</li>
<li>Meals and refreshments</li>
<li>Transport support</li>
<li>Cloud or software credits</li>
<li>Printing and learning materials</li>
<li>Photography and media support</li>
<li>Mentors and technical volunteers</li>
</ul>
<a href="/contact/" class="btn">Contact us</a>
<h2>They Already Support Us!</h2>
<p>(Display approved partner logos under the partner categories used on the homepage.)</p>
<h2>Current Work That Will Benefit From Your Support</h2>
<h3>Free Local Workshops</h3>
<p>Help local volunteer teams deliver well organised, beginner friendly Python and AI workshops without charging participants.</p>
<h3>Python and AI Tutorial</h3>
<p>Support the development and maintenance of a clear, practical tutorial that participants can use during workshops and continue using afterwards.</p>
<h3>Organiser and Mentor Resources</h3>
<p>Help us equip local organisers and mentors with guidance that protects programme quality and creates a supportive experience for beginners.</p>
<h3>Access and Participation</h3>
<p>Support participants who may need access to devices, internet, transport, meals or other practical assistance to attend and complete a workshop.</p>"""
        ),
        (
            "/partners/",
            "Our Partners",
            """<h1>Our Partners</h1>
<p>Our partners are organisations that support Python Weekend through programme sponsorship, local event sponsorship or approved in kind contributions.</p>
<p>They help us create free learning opportunities, strengthen our resources and support volunteer teams bringing beginner Python and AI workshops to their communities.</p>
<p>Would your organisation like to join them?</p>
<a href="/contact/" class="btn">Contact us about partnership</a>"""
        ),
        (
            "/organise/",
            "Organise a Python Weekend Workshop",
            """<h1>Organise a Python Weekend Workshop</h1>
<p>Python Weekend events are organised by groups of committed volunteers in local communities.</p>
<p>Official workshops are designed for complete beginners and are provided free to selected participants. Attendees do not need previous programming experience. They need access to a laptop, basic computer skills, curiosity and a willingness to learn.</p>
<p>Local teams receive a shared programme framework and organiser guidance. Every workshop must follow the Python Weekend brand standards, learning objectives and Code of Conduct.</p>
<h2>In Person Workshops</h2>
<p>An in person workshop brings participants, mentors and organisers together in one physical location.</p>
<p>Participants can work in small groups, receive face to face support and build relationships with other learners in their city. Organisers are responsible for choosing a safe, accessible venue and planning for internet, electricity, participant welfare and equipment needs.</p>
<h2>Remote Workshops</h2>
<p>A remote workshop is delivered online, with participants, mentors and organisers joining from different locations.</p>
<p>This format may be suitable when travel, venue, safety, cost or geography makes an in person workshop difficult. Remote organisers must plan carefully for communication, technical support, internet limitations and participant engagement.</p>
<h2>The Value of Organising Python Weekend</h2>
<ul>
<li>Join a supportive community of organisers, mentors and technology educators</li>
<li>Give complete beginners a practical entry into Python and AI</li>
<li>Strengthen the technology community in your city</li>
<li>Create opportunities for women and other underserved groups to participate</li>
<li>Develop leadership, programme management and community building experience</li>
<li>Help participants move from curiosity to their first working project</li>
</ul>
<a href="/contact/" class="btn">Apply to organise a workshop &raquo;</a>
<h2>Resources for Organisers</h2>
<ul>
<li>Python Weekend Organiser's Manual</li>
<li>Python Weekend Mentoring Guide</li>
<li>Media and brand resources</li>
<li>Python and AI Workshop Tutorial</li>
<li>Local sponsorship guidance</li>
<li>Organiser community channel</li>
</ul>"""
        ),
        (
            "/contribute/",
            "Contribute",
            """<h1>Contribute</h1>
<p>There are many ways to contribute to Python Weekend. You can organise an event, mentor beginners, improve the tutorial, support the website, translate resources or help a local workshop succeed.</p>
<p>If you would rather provide financial or in kind support, you can sponsor a local event or contact the central team about a wider partnership.</p>
<h2>Support Us!</h2>
<p>Python Weekend workshops depend on partners who help local teams provide a strong learning experience at no cost to participants.</p>
<p>Individuals and organisations can support a specific event by contacting its local organising team. Wider programme partnerships should be discussed with the central Python Weekend team.</p>
<a href="/support-us/">Support a workshop &raquo;</a>
<h2>Organise!</h2>
<p>Each Python Weekend event is a practical beginner workshop focused on Python foundations and an introduction to building with AI.</p>
<p>Local organisers build a volunteer team, secure a suitable venue or remote platform, recruit mentors, select participants, manage event communication and deliver the programme using official resources.</p>
<p>Ready to begin? Read the Organiser's Manual and apply to bring Python Weekend to your city.</p>
<a href="/organise/">Organise a workshop &raquo;</a>
<h2>Mentor!</h2>
<p>Have you seen a Python Weekend event happening in your city and want to help? Contact the local organising team and ask whether they need mentors.</p>
<p>Mentors guide a small group of beginners through the workshop tutorial, help participants understand errors and encourage them to solve problems independently.</p>
<p>You do not need to know everything. You need a sound understanding of the workshop material, patience, empathy and a willingness to guide without taking over.</p>
<a href="/resources/">Read the Mentoring Guide &raquo;</a>
<h2>Work on the Website!</h2>
<p>There is always something that can make the Python Weekend website clearer, faster and more useful.</p>
<p>Contributors may report or fix bugs, correct typographical errors, improve accessibility, update documentation or help develop approved features.</p>
<a href="https://github.com/SKY-MORALES7/PYTHON-WEEKEND" target="_blank">View the website repository &raquo;</a>
<h2>Want to Do More?</h2>
<p>If you have an idea that is not listed here, contact us and explain what you would like to contribute.</p>
<a href="/contact/">Contact the Python Weekend team &raquo;</a>"""
        ),
        (
            "/resources/",
            "Resources",
            """<h1>Resources</h1>
<p>Python Weekend resources are designed to help complete beginners learn during a workshop and continue practising afterwards.</p>
<p>The official tutorial, organiser resources and mentoring guidance should be made publicly available when they are ready. Each resource must display its current version, ownership and licence clearly.</p>

<h2>Python and AI Tutorial</h2>
<p>The tutorial used during Python Weekend workshops.</p>
<p>It introduces the learning environment, Python foundations, problem solving, working with simple data and a guided beginner AI project. It should be written in plain language and designed for someone learning to program for the first time.</p>
<a href="/content/tutorials/">Read it &raquo;</a>

<h2>Organiser's Manual</h2>
<p>A practical handbook containing what local teams need to plan and deliver an official Python Weekend workshop.</p>
<p>It should cover team formation, approval, budgeting, sponsorship, venue selection, participant applications, mentor recruitment, communication, safety, event delivery and post event reporting.</p>

<h2>Mentoring Guide</h2>
<p>Good mentoring is central to the Python Weekend experience.</p>
<p>This guide should explain how to support beginners, ask useful questions, respond to errors, work with different learning speeds and create a respectful environment without writing participants' projects for them.</p>

<h2>Tutorial Extensions</h2>
<p>Additional exercises and projects for participants who complete the main tutorial or want to continue learning after the workshop.</p>
<p>Extensions may cover automation, data analysis, web applications, AI APIs and responsible AI practice. The main workshop tutorial should remain achievable within one weekend.</p>"""
        ),
        (
            "/faq/",
            "FAQ: Frequently Asked Questions",
            """<h1>FAQ: Frequently Asked Questions</h1>
<p>Python Weekend workshops are organised in different cities, and many people ask similar questions. If your question is not answered here, please contact us.</p>

<h2>Python Weekend Workshops</h2>
<h3>How can I register?</h3>
<p>Find the workshop happening in your city and open its event page. If applications are open, you will see an application link. If no application link is displayed, registration has not opened or has already closed.</p>
<h3>I missed the deadline. Can I still apply?</h3>
<p>Usually not. Local teams need time to review applications, confirm participants and prepare the workshop. You can subscribe to the newsletter to hear about future events.</p>
<h3>I want to mentor or sponsor an event. What should I do?</h3>
<p>Contact the local organising team through the event page. They will tell you what support is needed.</p>
<h3>I am following the tutorial and my code is not working. Can the central team debug it for me?</h3>
<p>The central team primarily supports local organisers and maintains programme resources. Use the official community support channel when available, or ask for help through the relevant workshop community.</p>

<h2>Python Weekend in General</h2>
<h3>Who is Python Weekend for?</h3>
<p>Python Weekend is for complete beginners who want to learn Python and understand how it can be used in artificial intelligence. Students, professionals, founders, creatives, job seekers and people changing careers are welcome to apply.</p>
<h3>Is Python Weekend only for women?</h3>
<p>No. Python Weekend welcomes people of all genders. We intentionally encourage women and people from communities with limited access to technology education because a more inclusive learning environment strengthens the technology community.</p>
<h3>Is Python Weekend inclusive of transgender and nonbinary people?</h3>
<p>Yes. Python Weekend welcomes people of every gender identity. All participants, mentors, organisers and partners must follow the Code of Conduct.</p>
<h3>Is there an age limit?</h3>
<p>Eligibility may vary by local event. Check the relevant event page before applying. Where minors are accepted, the local team must state any consent or safeguarding requirements.</p>
<h3>Is Python Weekend free?</h3>
<p>Official Python Weekend workshops are free to selected participants. Local teams may secure sponsors and partners to cover the cost of delivering the event.</p>
<h3>Do I need previous programming experience?</h3>
<p>No. The workshop is designed for people who are learning to program for the first time.</p>
<h3>Will I become a Python or AI expert in one weekend?</h3>
<p>No. Python Weekend provides a practical beginning. You will learn essential concepts, complete a guided project and leave with a clearer path for continued learning.</p>
<h3>Can I organise Python Weekend in my city?</h3>
<p>Yes. Read the Organiser's Manual and submit an application to organise a workshop. Approval is required before using the Python Weekend name and brand for an event.</p>"""
        ),
        (
            "/about/",
            "About Python Weekend",
            """<h1>About Python Weekend</h1>
<p>Python Weekend is an initiative of Code Campus International created to make Python and artificial intelligence more approachable for complete beginners.</p>
<p>Our goal is to advance practical technology education by supporting free beginner workshops, developing accessible learning materials and helping volunteer teams create welcoming first experiences with programming.</p>
<p>Python Weekend does this by:</p>
<ul>
<li>Supporting free, practical Python and AI workshops</li>
<li>Creating beginner learning resources</li>
<li>Equipping local organisers and mentors</li>
<li>Encouraging women and underserved groups to participate in technology</li>
<li>Highlighting relatable Python and AI role models</li>
<li>Helping participants identify clear next steps after the workshop</li>
</ul>
<p>Python Weekend was shaped by Mayokun Adeoti's experience organising and coaching at seven editions of Django Girls Abuja. It applies the lessons of patient mentorship, accessible learning and community led delivery to a broader beginner programme focused on Python and AI.</p>
<p>Python Weekend is independently operated by Code Campus International. It is not a Django Girls event and should not be presented as an official programme of Django Girls or the Django Software Foundation.</p>
<h2>Initiative Details</h2>
<p><strong>Official name:</strong> Python Weekend<br>
<strong>Parent organisation:</strong> Code Campus International<br>
<strong>Website:</strong> pythonweekend.org<br>
<strong>Email:</strong> hello@pythonweekend.org<br>
<strong>Programme office:</strong> Suite 207, DBM Plaza, Aminu Kano Crescent, Wuse 2, Abuja, Nigeria</p>
<h2>Who Owns Python Weekend?</h2>
<p>Python Weekend is an initiative and brand of Code Campus International. Its community includes the local organisers, mentors, contributors, participants and partners who help deliver its mission.</p>
<p>Approval from Code Campus International is required before using the Python Weekend name or brand to organise an official event.</p>
<h2>How Can I Support Python Weekend?</h2>
<p>You can support a local workshop, provide approved in kind assistance or discuss a wider programme partnership with the central team.</p>
<p><a href="/support-us/">Support a workshop</a> &bull; <a href="/content/events/">View events</a> &bull; <a href="/contact/">Contact us</a></p>
<h2>More Information</h2>
<p>If you would like to learn more about Python Weekend or discuss a partnership, contact us at <strong>hello@pythonweekend.org</strong>.</p>"""
        ),
        (
            "/code-of-conduct/",
            "Code of Conduct",
            """<h1>Code of Conduct</h1>
<p>Python Weekend should be a welcoming place where people learn, ask questions and meet others in a friendly environment.</p>
<p>All attendees, mentors, speakers, organisers, volunteers, partners, exhibitors and visitors are required to treat one another with respect and follow this Code of Conduct before, during and after every Python Weekend activity.</p>
<h2>In Short</h2>
<ul>
<li>Python Weekend is committed to a harassment free experience for everyone, regardless of gender, gender identity, sexual orientation, disability, physical appearance, body size, age, ethnicity, race, religion, nationality, level of experience or background.</li>
<li>Harassment, discrimination, intimidation and unwanted sexual attention are not tolerated.</li>
<li>Sexualised language or imagery is not appropriate in workshop content, communication channels or event spaces.</li>
<li>Be kind. Do not insult, shame or deliberately exclude other people.</li>
<li>Ask for consent before photographing, recording or publishing information about another person.</li>
<li>Respect privacy, personal boundaries and different learning speeds.</li>
<li>Participants who violate these rules may be warned, removed from an event or excluded from future Python Weekend activities.</li>
</ul>
<h2>Longer Version</h2>
<p>Harassment includes offensive comments, discriminatory jokes, deliberate intimidation, stalking, unwanted following, harassing photography or recording, repeated disruption, inappropriate physical contact, threats and unwelcome sexual attention.</p>
<p>It also includes conduct that targets a person because of gender, gender identity, sexual orientation, disability, physical appearance, body size, age, ethnicity, race, religion, nationality, technical ability or another personal characteristic.</p>
<p>Anyone asked to stop inappropriate behaviour must comply immediately.</p>
<p>Choose your words carefully. Sexist, racist, ableist or otherwise exclusionary comments and jokes can harm people and are not acceptable at Python Weekend.</p>
<p>If someone engages in harmful or disruptive behaviour, organisers may take any action they consider necessary to protect the community. This may include a private warning, removal from the workshop, exclusion from online channels or restriction from future events.</p>
<p>These expectations apply at event venues, online sessions, community channels, social activities connected to the workshop and all official Python Weekend communication.</p>
<h2>Reporting a Concern</h2>
<p>If you experience or witness harassment, or have another safety concern, contact a mentor or organiser immediately.</p>
<p>If your concern involves the local organising team, send the details privately to <strong>hello@pythonweekend.org</strong>.</p>
<p>Reports should be handled promptly, discreetly and with respect for the people involved. The organising team may help an affected person contact venue security, emergency services, local authorities or another appropriate source of assistance where necessary.</p>
<p>We value your presence and want you to feel safe while participating in Python Weekend.</p>"""
        ),
        (
            "/jobs/",
            "Job Board",
            """<h1>Job Board</h1>
<h3>Sorry, there are no job openings at the moment.</h3>
<p>When approved Python, AI or entry level technology opportunities are available, they may be displayed on this page.</p>"""
        ),
        (
            "/terms/",
            "Terms and Conditions",
            """<h1>Terms and Conditions</h1>
<p>The final terms should address:</p>
<ul>
<li>Ownership and operation of pythonweekend.org</li>
<li>Acceptance of the website terms</li>
<li>Event applications and participant selection</li>
<li>Accuracy of event information</li>
<li>Use of Python Weekend learning materials</li>
<li>Acceptable use of the website and community features</li>
<li>Use of the Python Weekend name, logo and brand</li>
<li>Submitted content, photographs and consent</li>
<li>External websites and third party services</li>
<li>Availability of the website and programme</li>
<li>Disclaimer and limitation provisions appropriate to Nigerian law</li>
<li>Changes to the terms</li>
<li>Contact information</li>
</ul>"""
        ),
        (
            "/privacy/",
            "Privacy and Cookies Policy",
            """<h1>Privacy and Cookies Policy</h1>
<p>The final policy should explain:</p>
<ul>
<li>What personal information is collected</li>
<li>Information collected through participant, mentor and organiser applications</li>
<li>Newsletter subscription data</li>
<li>Contact form data</li>
<li>Event photographs and consent</li>
<li>Cookies, analytics and embedded media</li>
<li>Why the information is used</li>
<li>Who can access it, including approved local organisers and service providers</li>
<li>How long different records are retained</li>
<li>Data security measures</li>
<li>Participant rights and how to make a request</li>
<li>Children's or minors' data, if any edition accepts minors</li>
<li>International data transfers, if applicable</li>
<li>Policy changes</li>
<li>Contact information for privacy questions</li>
</ul>"""
        )
    ]

    for url, title, content in pages:
        create_or_update_flatpage(url, title, content)

if __name__ == "__main__":
    run()
