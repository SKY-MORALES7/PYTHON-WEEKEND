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
            "/about/",
            "About Python Weekend",
            """<!-- Hero -->
<section style="background:var(--py-navy);padding:5rem 1.5rem 4rem;text-align:center;">
  <div style="max-width:760px;margin:0 auto;">
    <h1 style="font-family:'Rajdhani',sans-serif;font-size:clamp(2rem,5vw,3rem);font-weight:700;color:var(--py-yellow);margin-bottom:1rem;">About Python Weekend</h1>
    <p class="font-body text-slate-100 text-base leading-relaxed font-medium" style="max-width:600px;margin:0 auto;color:rgba(255,255,255,0.85);">
      An initiative of Code Campus International created to make Python and artificial intelligence more approachable for complete beginners.
    </p>
  </div>
</section>

<!-- What We Do -->
<section class="section-dg">
  <div class="container-dg">
    <div class="about-grid">

      <div>
        <h2>About Python Weekend</h2>
        <p style="margin-bottom:1rem;">
          Python Weekend is an initiative of Code Campus International created to make Python and artificial intelligence more approachable for complete beginners.
        </p>
        <p style="margin-bottom:1rem;">
          Our goal is to advance practical technology education by supporting free beginner workshops, developing accessible learning materials and helping volunteer teams create welcoming first experiences with programming.
        </p>
        <p style="margin-bottom:1.5rem;">Python Weekend does this by:</p>
        <ul style="list-style:none;padding:0;margin:0;display:flex;flex-direction:column;gap:0.75rem;margin-bottom:1.5rem;">
          <li style="display:flex;align-items:flex-start;gap:0.75rem;"><span style="color:var(--py-blue);">✓</span><span>Supporting free, practical Python and AI workshops</span></li>
          <li style="display:flex;align-items:flex-start;gap:0.75rem;"><span style="color:var(--py-blue);">✓</span><span>Creating beginner learning resources</span></li>
          <li style="display:flex;align-items:flex-start;gap:0.75rem;"><span style="color:var(--py-blue);">✓</span><span>Equipping local organisers and mentors</span></li>
          <li style="display:flex;align-items:flex-start;gap:0.75rem;"><span style="color:var(--py-blue);">✓</span><span>Encouraging women and underserved groups to participate in technology</span></li>
          <li style="display:flex;align-items:flex-start;gap:0.75rem;"><span style="color:var(--py-blue);">✓</span><span>Highlighting relatable Python and AI role models</span></li>
          <li style="display:flex;align-items:flex-start;gap:0.75rem;"><span style="color:var(--py-blue);">✓</span><span>Helping participants identify clear next steps after the workshop</span></li>
        </ul>
        <p style="color:var(--py-navy);line-height:1.625;font-size:1rem;font-weight:500;">
          Python Weekend was shaped by Mayokun Adeoti's experience organising and coaching beginner tech events in Abuja. It applies the lessons of patient mentorship, accessible learning and community-led delivery to a broader beginner programme focused on Python and AI.
        </p>
      </div>

      <div>
        <h2>Initiative Details</h2>
        <dl style="display:flex;flex-direction:column;gap:1rem;">
          <div>
            <dt style="font-size:0.8rem;text-transform:uppercase;letter-spacing:0.05em;color:var(--py-muted);margin-bottom:0.25rem;">Official name</dt>
            <dd style="font-weight:600;color:var(--py-navy);">Python Weekend</dd>
          </div>
          <div>
            <dt style="font-size:0.8rem;text-transform:uppercase;letter-spacing:0.05em;color:var(--py-muted);margin-bottom:0.25rem;">Parent organisation</dt>
            <dd style="font-weight:600;color:var(--py-navy);">Code Campus International</dd>
          </div>
          <div>
            <dt style="font-size:0.8rem;text-transform:uppercase;letter-spacing:0.05em;color:var(--py-muted);margin-bottom:0.25rem;">Website</dt>
            <dd><a href="https://pythonweekend.org" style="color:var(--py-blue);">pythonweekend.org</a></dd>
          </div>
          <div>
            <dt style="font-size:0.8rem;text-transform:uppercase;letter-spacing:0.05em;color:var(--py-muted);margin-bottom:0.25rem;">Email</dt>
            <dd><a href="mailto:hello@pythonweekend.org" style="color:var(--py-blue);">hello@pythonweekend.org</a></dd>
          </div>
          <div>
            <dt style="font-size:0.8rem;text-transform:uppercase;letter-spacing:0.05em;color:var(--py-muted);margin-bottom:0.25rem;">Programme office</dt>
            <dd style="color:var(--py-navy);line-height:1.625;font-size:1rem;font-weight:500;">Suite 207, DBM Plaza<br>Aminu Kano Crescent<br>Wuse 2, Abuja, Nigeria</dd>
          </div>
        </dl>
      </div>

    </div>
  </div>
</section>

<!-- Ownership -->
<section class="section-dg" style="background:var(--py-light);">
  <div class="container-dg">
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:2rem;">

      <div class="card-brutal p-8" style="background:#fff;border:2.5px solid #16213e;box-shadow:5px 5px 0px #16213e;">
        <h3 style="font-family:'Rajdhani',sans-serif;font-size:1.35rem;font-weight:700;color:var(--py-navy);margin-bottom:0.75rem;">Who Owns Python Weekend?</h3>
        <p style="color:var(--py-navy);font-size:1rem;line-height:1.625;font-weight:500;">
          Python Weekend is an initiative and brand of Code Campus International. Its community includes the local organisers, mentors, contributors, participants and partners who help deliver its mission.
        </p>
        <p style="color:var(--py-navy);font-size:1rem;line-height:1.625;font-weight:500;margin-top:0.75rem;">
          Approval from Code Campus International is required before using the Python Weekend name or brand to organise an official event.
        </p>
      </div>

      <div class="card-brutal p-8" style="background:#fff;border:2.5px solid #16213e;box-shadow:5px 5px 0px #16213e;">
        <h3 style="font-family:'Rajdhani',sans-serif;font-size:1.35rem;font-weight:700;color:var(--py-navy);margin-bottom:0.75rem;">How Can I Support Python Weekend?</h3>
        <p style="color:var(--py-navy);font-size:1rem;line-height:1.625;font-weight:500;margin-bottom:1rem;">
          You can support a local workshop, provide approved in-kind assistance or discuss a wider programme partnership with the central team.
        </p>
        <div style="display:flex;flex-direction:column;gap:0.5rem;">
          <a href="/support/" style="color:var(--py-blue);font-size:0.95rem;font-weight:700;">Support a workshop »</a>
          <a href="/content/events/" style="color:var(--py-blue);font-size:0.95rem;font-weight:700;">View events »</a>
          <a href="/contact/" style="color:var(--py-blue);font-size:0.95rem;font-weight:700;">Contact us »</a>
        </div>
      </div>

      <div class="card-brutal p-8" style="background:#fff;border:2.5px solid #16213e;box-shadow:5px 5px 0px #16213e;">
        <h3 style="font-family:'Rajdhani',sans-serif;font-size:1.35rem;font-weight:700;color:var(--py-navy);margin-bottom:0.75rem;">Independence Statement</h3>
        <p style="color:var(--py-navy);font-size:1rem;line-height:1.625;font-weight:500;">
          Python Weekend is independently operated by Code Campus International.
        </p>
      </div>

    </div>
  </div>
</section>

<!-- More Information -->
<section class="section-dg" style="text-align:center;">
  <div class="container-dg" style="max-width:580px;">
    <h2>More Information</h2>
    <p style="color:var(--py-navy);margin-bottom:1.5rem;font-size:1rem;line-height:1.625;font-weight:500;">If you would like to learn more about Python Weekend or discuss a partnership, contact us at hello@pythonweekend.org.</p>
    <a href="/contact/" class="btn-orange" style="display:inline-block;">Contact us</a>
  </div>
</section>"""
        ),
        (
            "/code-of-conduct/",
            "Code of Conduct",
            """<!-- Hero -->
<section style="background:var(--py-navy);padding:5rem 1.5rem 4rem;text-align:center;">
  <div style="max-width:720px;margin:0 auto;">
    <h1 style="font-family:'Rajdhani',sans-serif;font-size:clamp(2rem,5vw,3rem);font-weight:700;color:var(--py-yellow);margin-bottom:1rem;">Code of Conduct</h1>
    <p style="font-size:1.05rem;color:rgba(255,255,255,0.75);line-height:1.7;max-width:560px;margin:0 auto;">
      Python Weekend should be a welcoming place where people learn, ask questions and meet others in a friendly environment.
    </p>
  </div>
</section>

<section class="section-dg">
  <div class="container-dg" style="max-width:820px;">

    <p style="color:var(--py-body);line-height:1.8;margin-bottom:1.5rem;">
      All attendees, mentors, speakers, organisers, volunteers, partners, exhibitors and visitors are required to treat one another with respect and follow this Code of Conduct before, during and after every Python Weekend activity.
    </p>

    <!-- In short -->
    <div style="background:var(--py-light);border-radius:1rem;padding:2rem;margin-bottom:2.5rem;">
      <h2 style="margin-top:0;margin-bottom:1.25rem;">In Short</h2>
      <ul style="list-style:none;padding:0;margin:0;display:flex;flex-direction:column;gap:0.85rem;">
        <li style="display:flex;align-items:flex-start;gap:0.75rem;"><span style="color:var(--py-blue);font-size:1rem;margin-top:0.1rem;">✓</span><span style="color:var(--py-body);line-height:1.6;">Python Weekend is committed to a harassment-free experience for everyone, regardless of gender, gender identity, sexual orientation, disability, physical appearance, body size, age, ethnicity, race, religion, nationality, level of experience or background.</span></li>
        <li style="display:flex;align-items:flex-start;gap:0.75rem;"><span style="color:var(--py-blue);">✓</span><span style="color:var(--py-body);line-height:1.6;">Harassment, discrimination, intimidation and unwanted sexual attention are not tolerated.</span></li>
        <li style="display:flex;align-items:flex-start;gap:0.75rem;"><span style="color:var(--py-blue);">✓</span><span style="color:var(--py-body);line-height:1.6;">Sexualised language or imagery is not appropriate in workshop content, communication channels or event spaces.</span></li>
        <li style="display:flex;align-items:flex-start;gap:0.75rem;"><span style="color:var(--py-blue);">✓</span><span style="color:var(--py-body);line-height:1.6;">Be kind. Do not insult, shame or deliberately exclude other people.</span></li>
        <li style="display:flex;align-items:flex-start;gap:0.75rem;"><span style="color:var(--py-blue);">✓</span><span style="color:var(--py-body);line-height:1.6;">Ask for consent before photographing, recording or publishing information about another person.</span></li>
        <li style="display:flex;align-items:flex-start;gap:0.75rem;"><span style="color:var(--py-blue);">✓</span><span style="color:var(--py-body);line-height:1.6;">Respect privacy, personal boundaries and different learning speeds.</span></li>
        <li style="display:flex;align-items:flex-start;gap:0.75rem;"><span style="color:var(--py-blue);">✓</span><span style="color:var(--py-body);line-height:1.6;">Participants who violate these rules may be warned, removed from an event or excluded from future Python Weekend activities.</span></li>
      </ul>
    </div>

    <!-- Longer version -->
    <h2>Longer Version</h2>
    <p style="color:var(--py-body);line-height:1.8;margin-bottom:1rem;">
      Harassment includes offensive comments, discriminatory jokes, deliberate intimidation, stalking, unwanted following, harassing photography or recording, repeated disruption, inappropriate physical contact, threats and unwelcome sexual attention.
    </p>
    <p style="color:var(--py-body);line-height:1.8;margin-bottom:1rem;">
      It also includes conduct that targets a person because of gender, gender identity, sexual orientation, disability, physical appearance, body size, age, ethnicity, race, religion, nationality, technical ability or another personal characteristic.
    </p>
    <p style="color:var(--py-body);line-height:1.8;margin-bottom:1rem;">
      Anyone asked to stop inappropriate behaviour must comply immediately.
    </p>
    <p style="color:var(--py-body);line-height:1.8;margin-bottom:1rem;">
      Choose your words carefully. Sexist, racist, ableist or otherwise exclusionary comments and jokes can harm people and are not acceptable at Python Weekend.
    </p>
    <p style="color:var(--py-body);line-height:1.8;margin-bottom:1rem;">
      If someone engages in harmful or disruptive behaviour, organisers may take any action they consider necessary to protect the community. This may include a private warning, removal from the workshop, exclusion from online channels or restriction from future events.
    </p>
    <p style="color:var(--py-body);line-height:1.8;margin-bottom:2rem;">
      These expectations apply at event venues, online sessions, community channels, social activities connected to the workshop and all official Python Weekend communication.
    </p>

    <!-- Reporting -->
    <div style="border-left:4px solid var(--py-blue);padding-left:1.5rem;margin-bottom:2rem;">
      <h2 style="margin-top:0;">Reporting a Concern</h2>
      <p style="color:var(--py-body);line-height:1.8;margin-bottom:1rem;">
        If you experience or witness harassment, or have another safety concern, contact a mentor or organiser immediately.
      </p>
      <p style="color:var(--py-body);line-height:1.8;margin-bottom:1rem;">
        If your concern involves the local organising team, send the details privately to <a href="mailto:hello@pythonweekend.org" style="color:var(--py-blue);">hello@pythonweekend.org</a>.
      </p>
      <p style="color:var(--py-body);line-height:1.8;">
        Reports should be handled promptly, discreetly and with respect for the people involved. The organising team may help an affected person contact venue security, emergency services, local authorities or another appropriate source of assistance where necessary.
      </p>
    </div>

    <p style="color:var(--py-body);line-height:1.8;font-style:italic;">
      We value your presence and want you to feel safe while participating in Python Weekend.
    </p>

  </div>
</section>"""
        ),
        (
            "/contribute/",
            "Contribute",
            """<!-- Hero -->
<section style="background:var(--py-navy);padding:5rem 1.5rem 4rem;text-align:center;">
  <div style="max-width:720px;margin:0 auto;">
    <h1 style="font-family:'Rajdhani',sans-serif;font-size:clamp(2rem,5vw,3rem);font-weight:700;color:var(--py-yellow);margin-bottom:1rem;">Contribute</h1>
    <p style="font-size:1.1rem;color:rgba(255,255,255,0.75);line-height:1.7;max-width:580px;margin:0 auto;">
      There are many ways to contribute to Python Weekend. Find the one that works for you.
    </p>
  </div>
</section>

<!-- Contribution paths -->
<section class="section-dg">
  <div class="container-dg">
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:2rem;">

      <!-- Support Us -->
      <div style="border-top:4px solid var(--py-yellow);padding-top:1.5rem;">
        <h2 style="font-family:'Rajdhani',sans-serif;font-size:1.35rem;font-weight:700;color:var(--py-navy);margin-bottom:0.75rem;">Support Us!</h2>
        <p style="color:var(--py-body);font-size:0.95rem;line-height:1.7;margin-bottom:1rem;">
          Python Weekend workshops depend on partners who help local teams provide a strong learning experience at no cost to participants. Individuals and organisations can support a specific event by contacting its local organising team. Wider programme partnerships should be discussed with the central Python Weekend team.
        </p>
        <a href="/support/" style="color:var(--py-blue);font-size:0.9rem;font-weight:600;">Support a workshop »</a>
      </div>

      <!-- Organise -->
      <div style="border-top:4px solid var(--py-blue);padding-top:1.5rem;">
        <h2 style="font-family:'Rajdhani',sans-serif;font-size:1.35rem;font-weight:700;color:var(--py-navy);margin-bottom:0.75rem;">Organise!</h2>
        <p style="color:var(--py-body);font-size:0.95rem;line-height:1.7;margin-bottom:1rem;">
          Each Python Weekend event is a practical beginner workshop focused on Python foundations and an introduction to building with AI. Local organisers build a volunteer team, secure a suitable venue or remote platform, recruit mentors, select participants, manage event communication and deliver the programme using official resources.
        </p>
        <p style="color:var(--py-body);font-size:0.9rem;line-height:1.6;margin-bottom:1rem;">Ready to begin? Read the Organiser's Manual and apply to bring Python Weekend to your city.</p>
        <a href="/organise/" style="color:var(--py-blue);font-size:0.9rem;font-weight:600;">Organise a workshop »</a>
      </div>

      <!-- Mentor -->
      <div style="border-top:4px solid var(--py-yellow);padding-top:1.5rem;">
        <h2 style="font-family:'Rajdhani',sans-serif;font-size:1.35rem;font-weight:700;color:var(--py-navy);margin-bottom:0.75rem;">Mentor!</h2>
        <p style="color:var(--py-body);font-size:0.95rem;line-height:1.7;margin-bottom:1rem;">
          Have you seen a Python Weekend event happening in your city and want to help? Contact the local organising team and ask whether they need mentors. Mentors guide a small group of beginners through the workshop tutorial, help participants understand errors and encourage them to solve problems independently.
        </p>
        <p style="color:var(--py-body);font-size:0.9rem;line-height:1.6;margin-bottom:1rem;">You do not need to know everything. You need a sound understanding of the workshop material, patience, empathy and a willingness to guide without taking over.</p>
        <a href="/resources/mentoring-guide/" style="color:var(--py-blue);font-size:0.9rem;font-weight:600;">Read the Mentoring Guide »</a>
      </div>

      <!-- Work on the Website -->
      <div style="border-top:4px solid var(--py-blue);padding-top:1.5rem;">
        <h2 style="font-family:'Rajdhani',sans-serif;font-size:1.35rem;font-weight:700;color:var(--py-navy);margin-bottom:0.75rem;">Work on the Website!</h2>
        <p style="color:var(--py-body);font-size:0.95rem;line-height:1.7;margin-bottom:1rem;">
          There is always something that can make the Python Weekend website clearer, faster and more useful. Contributors may report or fix bugs, correct typographical errors, improve accessibility, update documentation or help develop approved features.
        </p>
        <a href="https://github.com/SKY-MORALES7/PYTHON-WEEKEND" target="_blank" style="color:var(--py-blue);font-size:0.9rem;font-weight:600;">View the website repository »</a>
      </div>

      <!-- Improve the Tutorial -->
      <div style="border-top:4px solid var(--py-yellow);padding-top:1.5rem;">
        <h2 style="font-family:'Rajdhani',sans-serif;font-size:1.35rem;font-weight:700;color:var(--py-navy);margin-bottom:0.75rem;">Improve the Tutorial!</h2>
        <p style="color:var(--py-body);font-size:0.95rem;line-height:1.7;margin-bottom:1rem;">
          Is an explanation unclear? Did you find an error or an outdated instruction? You can help make the Python and AI tutorial easier for the next beginner. Approved contributions may correct mistakes, improve explanations, update installation steps, strengthen accessibility or add carefully reviewed exercises.
        </p>
        <a href="/resources/python-ai-tutorial/" style="color:var(--py-blue);font-size:0.9rem;font-weight:600;">Contribute to the tutorial »</a>
      </div>

      <!-- Translate -->
      <div style="border-top:4px solid var(--py-blue);padding-top:1.5rem;">
        <h2 style="font-family:'Rajdhani',sans-serif;font-size:1.35rem;font-weight:700;color:var(--py-navy);margin-bottom:0.75rem;">Translate the Tutorial!</h2>
        <p style="color:var(--py-body);font-size:0.95rem;line-height:1.7;margin-bottom:1rem;">
          Help more people learn in a language they understand. Translation teams can adapt approved Python Weekend learning resources while preserving the meaning, technical accuracy and inclusive tone of the original material.
        </p>
        <span style="color:var(--py-muted);font-size:0.85rem;font-style:italic;">Translation workflow link published when established.</span>
      </div>

    </div>

    <!-- Want to do more -->
    <div style="margin-top:3rem;padding:2rem;background:var(--py-light);border-radius:1rem;text-align:center;">
      <h3 style="font-family:'Rajdhani',sans-serif;font-size:1.25rem;font-weight:700;color:var(--py-navy);margin-bottom:0.75rem;">Want to Do More?</h3>
      <p style="color:var(--py-body);font-size:0.95rem;margin-bottom:1.25rem;">If you have an idea that is not listed here, contact us and explain what you would like to contribute.</p>
      <a href="/contact/" class="btn-orange" style="display:inline-block;">Contact the Python Weekend team »</a>
    </div>

  </div>
</section>"""
        ),
        (
            "/faq/",
            "FAQ: Frequently Asked Questions",
            """<!-- Hero -->
<section style="background:var(--py-navy);padding:5rem 1.5rem 4rem;text-align:center;">
  <div style="max-width:720px;margin:0 auto;">
    <h1 style="font-family:'Rajdhani',sans-serif;font-size:clamp(2rem,5vw,3rem);font-weight:700;color:var(--py-yellow);margin-bottom:1rem;">Frequently Asked Questions</h1>
    <p class="font-body text-slate-100 text-base leading-relaxed font-medium" style="max-width:560px;margin:0 auto;color:rgba(255,255,255,0.85);">
      Python Weekend workshops are organised in different cities, and many people ask similar questions. If your question is not answered here, please <a href="/contact/" style="color:var(--py-yellow);text-decoration:underline;font-weight:700;">contact us</a>.
    </p>
  </div>
</section>

<section class="section-dg">
  <div class="container-dg" style="max-width:820px;">

    <!-- Workshops -->
    <h2 style="margin-bottom:1.5rem;">Python Weekend Workshops</h2>

    <div style="display:flex;flex-direction:column;gap:0;">
      <details style="border-bottom:1.5px solid #16213e;padding:1.25rem 0;" open>
        <summary style="font-family:'Rajdhani',sans-serif;font-size:1.15rem;font-weight:700;color:var(--py-navy);cursor:pointer;list-style:none;display:flex;justify-content:space-between;align-items:center;gap:1rem;">Q: How can I register?<span style="font-size:1.2rem;flex-shrink:0;font-weight:800;">−</span></summary>
        <p style="margin-top:0.75rem;color:var(--py-navy);line-height:1.625;font-size:1rem;font-weight:500;">A: Find the workshop happening in your city and open its event page. If applications are open, you will see an application link. If no application link is displayed, registration has not opened or has already closed.</p>
      </details>

      <details style="border-bottom:1.5px solid #16213e;padding:1.25rem 0;">
        <summary style="font-family:'Rajdhani',sans-serif;font-size:1.15rem;font-weight:700;color:var(--py-navy);cursor:pointer;list-style:none;display:flex;justify-content:space-between;align-items:center;gap:1rem;">Q: I missed the deadline. Can I still apply?<span style="font-size:1.2rem;flex-shrink:0;font-weight:800;">+</span></summary>
        <p style="margin-top:0.75rem;color:var(--py-navy);line-height:1.625;font-size:1rem;font-weight:500;">A: Usually not. Local teams need time to review applications, confirm participants and prepare the workshop. You can subscribe to the newsletter to hear about future events.</p>
      </details>

      <details style="border-bottom:1.5px solid #16213e;padding:1.25rem 0;">
        <summary style="font-family:'Rajdhani',sans-serif;font-size:1.15rem;font-weight:700;color:var(--py-navy);cursor:pointer;list-style:none;display:flex;justify-content:space-between;align-items:center;gap:1rem;">Q: I want to mentor or sponsor an event. What should I do?<span style="font-size:1.2rem;flex-shrink:0;font-weight:800;">+</span></summary>
        <p style="margin-top:0.75rem;color:var(--py-navy);line-height:1.625;font-size:1rem;font-weight:500;">A: Contact the local organising team through the event page. They will tell you what support is needed.</p>
      </details>

      <details style="border-bottom:1.5px solid #16213e;padding:1.25rem 0;">
        <summary style="font-family:'Rajdhani',sans-serif;font-size:1.15rem;font-weight:700;color:var(--py-navy);cursor:pointer;list-style:none;display:flex;justify-content:space-between;align-items:center;gap:1rem;">Q: I am following the tutorial and my code is not working. Can the central team debug it?<span style="font-size:1.2rem;flex-shrink:0;font-weight:800;">+</span></summary>
        <p style="margin-top:0.75rem;color:var(--py-navy);line-height:1.625;font-size:1rem;font-weight:500;">A: The central team primarily supports local organisers and maintains programme resources. Use the official community support channel when available, or ask for help through the relevant workshop community.</p>
      </details>
    </div>

    <!-- General -->
    <h2 style="margin-top:3.5rem;margin-bottom:1.5rem;">Python Weekend in General</h2>

    <div style="display:flex;flex-direction:column;gap:0;">
      <details style="border-bottom:1.5px solid #16213e;padding:1.25rem 0;">
        <summary style="font-family:'Rajdhani',sans-serif;font-size:1.15rem;font-weight:700;color:var(--py-navy);cursor:pointer;list-style:none;display:flex;justify-content:space-between;align-items:center;gap:1rem;">Q: Who is Python Weekend for?<span style="font-size:1.2rem;flex-shrink:0;font-weight:800;">+</span></summary>
        <p style="margin-top:0.75rem;color:var(--py-navy);line-height:1.625;font-size:1rem;font-weight:500;">A: Python Weekend is for complete beginners who want to learn Python and understand how it can be used in artificial intelligence. Students, professionals, founders, creatives, job seekers and people changing careers are welcome to apply.</p>
      </details>

      <details style="border-bottom:1.5px solid #16213e;padding:1.25rem 0;">
        <summary style="font-family:'Rajdhani',sans-serif;font-size:1.15rem;font-weight:700;color:var(--py-navy);cursor:pointer;list-style:none;display:flex;justify-content:space-between;align-items:center;gap:1rem;">Q: Is Python Weekend only for women?<span style="font-size:1.2rem;flex-shrink:0;font-weight:800;">+</span></summary>
        <p style="margin-top:0.75rem;color:var(--py-navy);line-height:1.625;font-size:1rem;font-weight:500;">A: No. Python Weekend welcomes people of all genders. We intentionally encourage women and people from communities with limited access to technology education because a more inclusive learning environment strengthens the technology community.</p>
      </details>

      <details style="border-bottom:1.5px solid #16213e;padding:1.25rem 0;">
        <summary style="font-family:'Rajdhani',sans-serif;font-size:1.15rem;font-weight:700;color:var(--py-navy);cursor:pointer;list-style:none;display:flex;justify-content:space-between;align-items:center;gap:1rem;">Q: Is Python Weekend inclusive of transgender and nonbinary people?<span style="font-size:1.2rem;flex-shrink:0;font-weight:800;">+</span></summary>
        <p style="margin-top:0.75rem;color:var(--py-navy);line-height:1.625;font-size:1rem;font-weight:500;">A: Yes. Python Weekend welcomes people of every gender identity. All participants, mentors, organisers and partners must follow the Code of Conduct.</p>
      </details>

      <details style="border-bottom:1.5px solid #16213e;padding:1.25rem 0;">
        <summary style="font-family:'Rajdhani',sans-serif;font-size:1.15rem;font-weight:700;color:var(--py-navy);cursor:pointer;list-style:none;display:flex;justify-content:space-between;align-items:center;gap:1rem;">Q: Is there an age limit?<span style="font-size:1.2rem;flex-shrink:0;font-weight:800;">+</span></summary>
        <p style="margin-top:0.75rem;color:var(--py-navy);line-height:1.625;font-size:1rem;font-weight:500;">A: Eligibility may vary by local event. Check the relevant event page before applying. Where minors are accepted, the local team must state any consent or safeguarding requirements.</p>
      </details>

      <details style="border-bottom:1.5px solid #16213e;padding:1.25rem 0;">
        <summary style="font-family:'Rajdhani',sans-serif;font-size:1.15rem;font-weight:700;color:var(--py-navy);cursor:pointer;list-style:none;display:flex;justify-content:space-between;align-items:center;gap:1rem;">Q: Is Python Weekend free?<span style="font-size:1.2rem;flex-shrink:0;font-weight:800;">+</span></summary>
        <p style="margin-top:0.75rem;color:var(--py-navy);line-height:1.625;font-size:1rem;font-weight:500;">A: Official Python Weekend workshops are free to selected participants. Local teams may secure sponsors and partners to cover the cost of delivering the event.</p>
      </details>

      <details style="border-bottom:1.5px solid #16213e;padding:1.25rem 0;">
        <summary style="font-family:'Rajdhani',sans-serif;font-size:1.15rem;font-weight:700;color:var(--py-navy);cursor:pointer;list-style:none;display:flex;justify-content:space-between;align-items:center;gap:1rem;">Q: Do I need previous programming experience?<span style="font-size:1.2rem;flex-shrink:0;font-weight:800;">+</span></summary>
        <p style="margin-top:0.75rem;color:var(--py-navy);line-height:1.625;font-size:1rem;font-weight:500;">A: No. The workshop is designed for people who are learning to program for the first time.</p>
      </details>

      <details style="border-bottom:1.5px solid #16213e;padding:1.25rem 0;">
        <summary style="font-family:'Rajdhani',sans-serif;font-size:1.15rem;font-weight:700;color:var(--py-navy);cursor:pointer;list-style:none;display:flex;justify-content:space-between;align-items:center;gap:1rem;">Q: Will I become a Python or AI expert in one weekend?<span style="font-size:1.2rem;flex-shrink:0;font-weight:800;">+</span></summary>
        <p style="margin-top:0.75rem;color:var(--py-navy);line-height:1.625;font-size:1rem;font-weight:500;">A: No. Python Weekend provides a practical beginning. You will learn essential concepts, complete a guided project and leave with a clearer path for continued learning.</p>
      </details>

      <details style="border-bottom:1.5px solid #16213e;padding:1.25rem 0;">
        <summary style="font-family:'Rajdhani',sans-serif;font-size:1.15rem;font-weight:700;color:var(--py-navy);cursor:pointer;list-style:none;display:flex;justify-content:space-between;align-items:center;gap:1rem;">Q: Can I organise Python Weekend in my city?<span style="font-size:1.2rem;flex-shrink:0;font-weight:800;">+</span></summary>
        <p style="margin-top:0.75rem;color:var(--py-navy);line-height:1.625;font-size:1rem;font-weight:500;">A: Yes. Read the Organiser's Manual and submit an application to organise a workshop. Approval is required before using the Python Weekend name and brand for an event. <a href="/applications/organize/" style="color:var(--py-blue);font-weight:700;text-decoration:underline;">Apply here »</a></p>
      </details>
    </div>

    <!-- Still need help -->
    <div class="card-brutal p-8 text-center mt-12" style="background:#fff;border:2.5px solid #16213e;box-shadow:5px 5px 0px #16213e;">
      <p style="color:var(--py-navy);margin-bottom:1rem;font-size:1rem;line-height:1.625;font-weight:500;">Still have a question not answered here?</p>
      <a href="/contact/" class="btn-orange" style="display:inline-block;">Contact us »</a>
    </div>

  </div>
</section>"""
        ),
        (
            "/jobs/",
            "Job Board",
            """<section style="background:var(--py-navy);padding:5rem 1.5rem 4rem;text-align:center;">
  <div style="max-width:720px;margin:0 auto;">
    <h1 style="font-family:'Rajdhani',sans-serif;font-size:clamp(2rem,5vw,3rem);font-weight:700;color:var(--py-yellow);margin-bottom:1rem;">Job Board</h1>
    <p style="font-size:1.05rem;color:rgba(255,255,255,0.75);line-height:1.7;max-width:560px;margin:0 auto;">
      Opportunities for Python, AI, and entry-level technology roles.
    </p>
  </div>
</section>

<section class="section-dg" style="text-align:center;padding:5rem 1.5rem;">
  <div class="container-dg" style="max-width:640px;">
    <div class="card-brutal p-10" style="background:#fff;border:2.5px solid #16213e;box-shadow:5px 5px 0px #16213e;">
      <div style="font-size:2.5rem;margin-bottom:1rem;">💼</div>
      <h2 style="font-family:'Rajdhani',sans-serif;font-size:1.5rem;font-weight:700;color:var(--py-navy);margin-bottom:1rem;">Sorry, there are no job openings at the moment.</h2>
      <p style="color:var(--py-body);line-height:1.7;font-size:1rem;margin-bottom:1.5rem;">
        When approved Python, AI, or entry-level technology opportunities are available, they will be displayed on this page.
      </p>
      <a href="/contact/" class="btn-orange" style="display:inline-block;">Contact us about listings »</a>
    </div>
  </div>
</section>"""
        ),
        (
            "/partners/",
            "Our Partners",
            """<section class="py-16 md:py-20 bg-white border-b-2.5 border-shield-navy relative overflow-hidden">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 text-center">
    <span class="font-mono text-xs font-bold uppercase tracking-widest text-white bg-shield-blue px-3 py-1.5 border-2 border-shield-navy inline-block mb-4 shadow-brutal-sm">
      Global Community Network
    </span>
    <h1 class="font-display font-bold text-4xl sm:text-6xl text-shield-navy uppercase tracking-tight mb-6 leading-none">
      Our Partners
    </h1>
    <p class="font-body text-shield-navy text-lg sm:text-xl font-medium leading-relaxed mb-8 max-w-2xl mx-auto">
      Our partners are organisations that support Python Weekend through programme sponsorship, local event sponsorship, or approved in-kind contributions. They help us create free learning opportunities, strengthen our resources, and support volunteer teams bringing beginner Python and AI workshops to their communities.
    </p>

    <div class="flex flex-wrap justify-center gap-5">
      <a href="/contact/" class="btn-brutal-hero group">
        <span class="font-display font-bold text-xl text-shield-navy uppercase tracking-wider">Contact Us About Partnership</span>
      </a>
    </div>
  </div>
</section>"""
        ),
        (
            "/resources/",
            "Resources",
            """<section style="background:var(--py-navy);padding:5rem 1.5rem 4rem;text-align:center;">
  <div style="max-width:720px;margin:0 auto;">
    <h1 style="font-family:'Rajdhani',sans-serif;font-size:clamp(2rem,5vw,3rem);font-weight:700;color:var(--py-yellow);margin-bottom:1rem;">Resources</h1>
    <p style="font-size:1.1rem;color:rgba(255,255,255,0.75);line-height:1.7;max-width:580px;margin:0 auto;">
      Python Weekend resources are designed to help complete beginners learn during a workshop and continue practising afterwards.
    </p>
  </div>
</section>

<section class="section-dg">
  <div class="container-dg">
    <p style="color:var(--py-body);line-height:1.7;font-size:1.05rem;margin-bottom:2.5rem;max-width:780px;">
      The official tutorial, organiser resources and mentoring guidance are made publicly available to help anyone learn Python and AI or bring a workshop to their city.
    </p>

    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:2rem;">

      <!-- Python and AI Tutorial -->
      <div class="card-brutal p-8" style="background:#fff;border:2.5px solid #16213e;box-shadow:5px 5px 0px #16213e;display:flex;flex-direction:column;justify-between;">
        <div>
          <div style="font-size:2rem;margin-bottom:1rem;">🐍</div>
          <h2 style="font-family:'Rajdhani',sans-serif;font-size:1.4rem;font-weight:700;color:var(--py-navy);margin-bottom:0.75rem;">Python and AI Tutorial</h2>
          <p style="color:var(--py-body);font-size:0.95rem;line-height:1.65;margin-bottom:1.5rem;">
            The tutorial used during Python Weekend workshops. It introduces the learning environment, Python foundations, problem solving, working with simple data and a guided beginner AI project.
          </p>
        </div>
        <a href="/resources/python-ai-tutorial/" style="color:var(--py-blue);font-weight:700;font-size:0.95rem;">Read it »</a>
      </div>

      <!-- Organiser's Manual -->
      <div class="card-brutal p-8" style="background:#fff;border:2.5px solid #16213e;box-shadow:5px 5px 0px #16213e;display:flex;flex-direction:column;justify-between;">
        <div>
          <div style="font-size:2rem;margin-bottom:1rem;">📖</div>
          <h2 style="font-family:'Rajdhani',sans-serif;font-size:1.4rem;font-weight:700;color:var(--py-navy);margin-bottom:0.75rem;">Organiser's Manual</h2>
          <p style="color:var(--py-body);font-size:0.95rem;line-height:1.65;margin-bottom:1.5rem;">
            A practical handbook containing what local teams need to plan and deliver an official Python Weekend workshop — from team formation to venue selection and delivery.
          </p>
        </div>
        <a href="/resources/organisers-manual/" style="color:var(--py-blue);font-weight:700;font-size:0.95rem;">Read it »</a>
      </div>

      <!-- Mentoring Guide -->
      <div class="card-brutal p-8" style="background:#fff;border:2.5px solid #16213e;box-shadow:5px 5px 0px #16213e;display:flex;flex-direction:column;justify-between;">
        <div>
          <div style="font-size:2rem;margin-bottom:1rem;">🧑‍🏫</div>
          <h2 style="font-family:'Rajdhani',sans-serif;font-size:1.4rem;font-weight:700;color:var(--py-navy);margin-bottom:0.75rem;">Mentoring Guide</h2>
          <p style="color:var(--py-body);font-size:0.95rem;line-height:1.65;margin-bottom:1.5rem;">
            Good mentoring is central to the Python Weekend experience. This guide explains how to support beginners, respond to errors, and foster a respectful environment.
          </p>
        </div>
        <a href="/resources/mentoring-guide/" style="color:var(--py-blue);font-weight:700;font-size:0.95rem;">Read it »</a>
      </div>

      <!-- Tutorial Extensions -->
      <div class="card-brutal p-8" style="background:#fff;border:2.5px solid #16213e;box-shadow:5px 5px 0px #16213e;display:flex;flex-direction:column;justify-between;">
        <div>
          <div style="font-size:2rem;margin-bottom:1rem;">🚀</div>
          <h2 style="font-family:'Rajdhani',sans-serif;font-size:1.4rem;font-weight:700;color:var(--py-navy);margin-bottom:0.75rem;">Tutorial Extensions</h2>
          <p style="color:var(--py-body);font-size:0.95rem;line-height:1.65;margin-bottom:1.5rem;">
            Additional exercises and projects for participants who complete the main tutorial or want to continue learning after the workshop.
          </p>
        </div>
        <a href="/resources/tutorial-extensions/" style="color:var(--py-blue);font-weight:700;font-size:0.95rem;">Read it »</a>
      </div>

    </div>
  </div>
</section>"""
        ),
        (
            "/support/",
            "Support a Workshop",
            """<!-- Hero -->
<section class="py-16 md:py-20 bg-white border-b-2.5 border-shield-navy relative overflow-hidden">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 text-center">
    <span class="font-mono text-xs font-bold uppercase tracking-widest text-white bg-shield-blue px-3 py-1.5 border-2 border-shield-navy inline-block mb-4 shadow-brutal-sm">
      Community Backers &amp; Impact
    </span>
    <h1 class="font-display font-bold text-4xl sm:text-6xl text-shield-navy uppercase tracking-tight mb-6 leading-none">
      Support a Workshop
    </h1>
    <p class="font-body text-shield-navy text-lg sm:text-xl font-medium leading-relaxed mb-8 max-w-2xl mx-auto">
      Python Weekend workshops are free to participants. Your support makes that possible.
    </p>
  </div>
</section>

<!-- Mission & Allocation -->
<section class="py-16 bg-shield-ice/20 border-b-2.5 border-shield-navy">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">

      <!-- Mission Card -->
      <div class="bg-white border-2.5 border-shield-navy p-8 sm:p-10 shadow-brutal flex flex-col justify-between">
        <div>
          <span class="font-mono text-xs font-bold uppercase tracking-widest text-white bg-shield-blue px-3 py-1 border-2 border-shield-navy inline-block mb-4 shadow-brutal-sm">
            Our Purpose
          </span>
          <h2 class="font-display font-bold text-3xl sm:text-4xl text-shield-navy uppercase tracking-tight mb-6">
            Our Mission
          </h2>
          <div class="space-y-4 font-body text-shield-navy text-base leading-relaxed font-medium">
            <p>
              Python Weekend helps complete beginners learn Python and take their first practical step into artificial intelligence through free, mentor-supported workshops.
            </p>
            <p>
              We support local volunteer teams with a shared programme framework, organiser guidance, learning resources, and central coordination. Partners make it possible for these teams to provide the spaces, tools, and participant support required for a strong learning experience.
            </p>
            <p>
              Our goal is to make Python and AI education more accessible, especially for individuals who have had limited opportunities to enter technology.
            </p>
            <p class="text-sm font-semibold text-shield-navy/80 border-t-2 border-shield-navy/20 pt-4">
              We are committed to transparency about the workshops and activities supported by our partners. Verified outcomes are published in periodic impact reports.
            </p>
          </div>
        </div>
      </div>

      <!-- Allocation Card -->
      <div class="bg-white border-2.5 border-shield-navy p-8 sm:p-10 shadow-brutal flex flex-col justify-between">
        <div>
          <span class="font-mono text-xs font-bold uppercase tracking-widest text-white bg-shield-blue px-3 py-1 border-2 border-shield-navy inline-block mb-4 shadow-brutal-sm">
            Direct Allocation
          </span>
          <h2 class="font-display font-bold text-3xl sm:text-4xl text-shield-navy uppercase tracking-tight mb-6">
            What Your Support Covers
          </h2>
          <ul class="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
            <li class="flex items-start gap-3 bg-shield-ice/40 border-2 border-shield-navy p-3 shadow-brutal-sm">
              <span class="w-6 h-6 bg-[#FFB800] border-1.5 border-shield-navy flex items-center justify-center font-bold text-shield-navy text-sm shrink-0">✓</span>
              <span class="font-body font-semibold text-shield-navy text-sm">Learning venues</span>
            </li>
            <li class="flex items-start gap-3 bg-shield-ice/40 border-2 border-shield-navy p-3 shadow-brutal-sm">
              <span class="w-6 h-6 bg-[#FFB800] border-1.5 border-shield-navy flex items-center justify-center font-bold text-shield-navy text-sm shrink-0">✓</span>
              <span class="font-body font-semibold text-shield-navy text-sm">Laptops and devices</span>
            </li>
            <li class="flex items-start gap-3 bg-shield-ice/40 border-2 border-shield-navy p-3 shadow-brutal-sm">
              <span class="w-6 h-6 bg-[#FFB800] border-1.5 border-shield-navy flex items-center justify-center font-bold text-shield-navy text-sm shrink-0">✓</span>
              <span class="font-body font-semibold text-shield-navy text-sm">Internet connectivity</span>
            </li>
            <li class="flex items-start gap-3 bg-shield-ice/40 border-2 border-shield-navy p-3 shadow-brutal-sm">
              <span class="w-6 h-6 bg-[#FFB800] border-1.5 border-shield-navy flex items-center justify-center font-bold text-shield-navy text-sm shrink-0">✓</span>
              <span class="font-body font-semibold text-shield-navy text-sm">Meals and refreshments</span>
            </li>
            <li class="flex items-start gap-3 bg-shield-ice/40 border-2 border-shield-navy p-3 shadow-brutal-sm">
              <span class="w-6 h-6 bg-[#FFB800] border-1.5 border-shield-navy flex items-center justify-center font-bold text-shield-navy text-sm shrink-0">✓</span>
              <span class="font-body font-semibold text-shield-navy text-sm">Transport support</span>
            </li>
            <li class="flex items-start gap-3 bg-shield-ice/40 border-2 border-shield-navy p-3 shadow-brutal-sm">
              <span class="w-6 h-6 bg-[#FFB800] border-1.5 border-shield-navy flex items-center justify-center font-bold text-shield-navy text-sm shrink-0">✓</span>
              <span class="font-body font-semibold text-shield-navy text-sm">Cloud &amp; software credits</span>
            </li>
            <li class="flex items-start gap-3 bg-shield-ice/40 border-2 border-shield-navy p-3 shadow-brutal-sm">
              <span class="w-6 h-6 bg-[#FFB800] border-1.5 border-shield-navy flex items-center justify-center font-bold text-shield-navy text-sm shrink-0">✓</span>
              <span class="font-body font-semibold text-shield-navy text-sm">Printing &amp; courseware</span>
            </li>
            <li class="flex items-start gap-3 bg-shield-ice/40 border-2 border-shield-navy p-3 shadow-brutal-sm">
              <span class="w-6 h-6 bg-[#FFB800] border-1.5 border-shield-navy flex items-center justify-center font-bold text-shield-navy text-sm shrink-0">✓</span>
              <span class="font-body font-semibold text-shield-navy text-sm">Photography &amp; media</span>
            </li>
          </ul>
        </div>
      </div>

    </div>
  </div>
</section>

<!-- How to Support -->
<section class="py-16 bg-white border-b-2.5 border-shield-navy">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="text-center mb-12">
      <span class="font-mono text-xs font-bold uppercase tracking-widest text-white bg-shield-blue px-3 py-1.5 border-2 border-shield-navy inline-block mb-3 shadow-brutal-sm">
        Get Involved
      </span>
      <h2 class="font-display font-bold text-3xl sm:text-5xl text-shield-navy uppercase tracking-tight">
        Start Supporting Python Weekend Today
      </h2>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-8">

      <div class="bg-white border-2.5 border-shield-navy p-8 shadow-brutal flex flex-col justify-between">
        <div>
          <div class="w-12 h-12 flex items-center justify-center bg-[#FFB800] border-2 border-shield-navy shadow-brutal-sm text-2xl mb-6">📍</div>
          <h3 class="font-display font-bold text-2xl text-shield-navy uppercase tracking-tight mb-4">Sponsor a Local Workshop</h3>
          <p class="font-body text-shield-navy text-base leading-relaxed font-medium mb-8">
            Support a specific Python Weekend edition by contacting its local organising team. Local sponsorship covers venue costs, internet access, participant meals, learning materials, and transport support.
          </p>
        </div>
        <a href="/content/events/" class="btn-brutal-cta">
          <span class="font-display font-bold text-base sm:text-lg text-shield-navy uppercase tracking-wider">View Upcoming Events</span>
        </a>
      </div>

      <div class="bg-white border-2.5 border-shield-navy p-8 shadow-brutal flex flex-col justify-between">
        <div>
          <div class="w-12 h-12 flex items-center justify-center bg-[#FFB800] border-2 border-shield-navy shadow-brutal-sm text-2xl mb-6">🤝</div>
          <h3 class="font-display font-bold text-2xl text-shield-navy uppercase tracking-tight mb-4">Become a Programme Partner</h3>
          <p class="font-body text-shield-navy text-base leading-relaxed font-medium mb-8">
            Companies and institutions can support multiple Python Weekend editions or contribute to resources used across the community — curriculum development, organiser training, website infrastructure, or accessibility.
          </p>
        </div>
        <a href="/contact/" class="btn-brutal-cta">
          <span class="font-display font-bold text-base sm:text-lg text-shield-navy uppercase tracking-wider">Discuss a Partnership</span>
        </a>
      </div>

      <div class="bg-white border-2.5 border-shield-navy p-8 shadow-brutal flex flex-col justify-between">
        <div>
          <div class="w-12 h-12 flex items-center justify-center bg-[#FFB800] border-2 border-shield-navy shadow-brutal-sm text-2xl mb-6">💡</div>
          <h3 class="font-display font-bold text-2xl text-shield-navy uppercase tracking-tight mb-4">Provide In-Kind Support</h3>
          <p class="font-body text-shield-navy text-base leading-relaxed font-medium mb-8">
            Your organisation can contribute venues, devices, internet connectivity, catering, transport vouchers, cloud credits, printing, or technical mentors — directly benefiting learners.
          </p>
        </div>
        <a href="/contact/" class="btn-brutal-cta">
          <span class="font-display font-bold text-base sm:text-lg text-shield-navy uppercase tracking-wider">Contact Us</span>
        </a>
      </div>

    </div>
  </div>
</section>

<!-- Current Work -->
<section class="py-16 bg-shield-ice/20 border-b-2.5 border-shield-navy">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="text-center mb-12">
      <span class="font-mono text-xs font-bold uppercase tracking-widest text-white bg-shield-blue px-3 py-1.5 border-2 border-shield-navy inline-block mb-3 shadow-brutal-sm">
        Community Initiatives
      </span>
      <h2 class="font-display font-bold text-3xl sm:text-5xl text-shield-navy uppercase tracking-tight">
        Current Work That Will Benefit From Your Support
      </h2>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">

      <div class="bg-white border-2.5 border-shield-navy border-t-6 border-t-shield-blue p-6 shadow-brutal">
        <h3 class="font-display font-bold text-xl text-shield-navy uppercase tracking-tight mb-3">Free Local Workshops</h3>
        <p class="font-body text-shield-navy text-sm font-medium leading-relaxed">
          Help local volunteer teams deliver well-organised, beginner-friendly Python and AI workshops without charging participants.
        </p>
      </div>

      <div class="bg-white border-2.5 border-shield-navy border-t-6 border-t-[#FFB800] p-6 shadow-brutal">
        <h3 class="font-display font-bold text-xl text-shield-navy uppercase tracking-tight mb-3">Python and AI Tutorial</h3>
        <p class="font-body text-shield-navy text-sm font-medium leading-relaxed">
          Support the development and maintenance of a clear, practical tutorial that participants can use during workshops and continue using afterwards.
        </p>
      </div>

      <div class="bg-white border-2.5 border-shield-navy border-t-6 border-t-shield-blue p-6 shadow-brutal">
        <h3 class="font-display font-bold text-xl text-shield-navy uppercase tracking-tight mb-3">Organiser &amp; Mentor Guides</h3>
        <p class="font-body text-shield-navy text-sm font-medium leading-relaxed">
          Help us equip local organisers and mentors with guidance that protects programme quality and creates a supportive experience for beginners.
        </p>
      </div>

      <div class="bg-white border-2.5 border-shield-navy border-t-6 border-t-[#FFB800] p-6 shadow-brutal">
        <h3 class="font-display font-bold text-xl text-shield-navy uppercase tracking-tight mb-3">Access &amp; Participation</h3>
        <p class="font-body text-shield-navy text-sm font-medium leading-relaxed">
          Support participants who need access to devices, internet, transport, meals or practical assistance to complete a workshop.
        </p>
      </div>

    </div>
  </div>
</section>"""
        ),
        (
            "/support-us/",
            "Support a Workshop",
            """<!-- Hero -->
<section class="py-16 md:py-20 bg-white border-b-2.5 border-shield-navy relative overflow-hidden">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 text-center">
    <span class="font-mono text-xs font-bold uppercase tracking-widest text-white bg-shield-blue px-3 py-1.5 border-2 border-shield-navy inline-block mb-4 shadow-brutal-sm">
      Community Backers &amp; Impact
    </span>
    <h1 class="font-display font-bold text-4xl sm:text-6xl text-shield-navy uppercase tracking-tight mb-6 leading-none">
      Support a Workshop
    </h1>
    <p class="font-body text-shield-navy text-lg sm:text-xl font-medium leading-relaxed mb-8 max-w-2xl mx-auto">
      Python Weekend workshops are free to participants. Your support makes that possible.
    </p>
  </div>
</section>

<!-- Mission & Allocation -->
<section class="py-16 bg-shield-ice/20 border-b-2.5 border-shield-navy">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">

      <!-- Mission Card -->
      <div class="bg-white border-2.5 border-shield-navy p-8 sm:p-10 shadow-brutal flex flex-col justify-between">
        <div>
          <span class="font-mono text-xs font-bold uppercase tracking-widest text-white bg-shield-blue px-3 py-1 border-2 border-shield-navy inline-block mb-4 shadow-brutal-sm">
            Our Purpose
          </span>
          <h2 class="font-display font-bold text-3xl sm:text-4xl text-shield-navy uppercase tracking-tight mb-6">
            Our Mission
          </h2>
          <div class="space-y-4 font-body text-shield-navy text-base leading-relaxed font-medium">
            <p>
              Python Weekend helps complete beginners learn Python and take their first practical step into artificial intelligence through free, mentor-supported workshops.
            </p>
            <p>
              We support local volunteer teams with a shared programme framework, organiser guidance, learning resources, and central coordination. Partners make it possible for these teams to provide the spaces, tools, and participant support required for a strong learning experience.
            </p>
            <p>
              Our goal is to make Python and AI education more accessible, especially for individuals who have had limited opportunities to enter technology.
            </p>
            <p class="text-sm font-semibold text-shield-navy/80 border-t-2 border-shield-navy/20 pt-4">
              We are committed to transparency about the workshops and activities supported by our partners. Verified outcomes are published in periodic impact reports.
            </p>
          </div>
        </div>
      </div>

      <!-- Allocation Card -->
      <div class="bg-white border-2.5 border-shield-navy p-8 sm:p-10 shadow-brutal flex flex-col justify-between">
        <div>
          <span class="font-mono text-xs font-bold uppercase tracking-widest text-white bg-shield-blue px-3 py-1 border-2 border-shield-navy inline-block mb-4 shadow-brutal-sm">
            Direct Allocation
          </span>
          <h2 class="font-display font-bold text-3xl sm:text-4xl text-shield-navy uppercase tracking-tight mb-6">
            What Your Support Covers
          </h2>
          <ul class="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
            <li class="flex items-start gap-3 bg-shield-ice/40 border-2 border-shield-navy p-3 shadow-brutal-sm">
              <span class="w-6 h-6 bg-[#FFB800] border-1.5 border-shield-navy flex items-center justify-center font-bold text-shield-navy text-sm shrink-0">✓</span>
              <span class="font-body font-semibold text-shield-navy text-sm">Learning venues</span>
            </li>
            <li class="flex items-start gap-3 bg-shield-ice/40 border-2 border-shield-navy p-3 shadow-brutal-sm">
              <span class="w-6 h-6 bg-[#FFB800] border-1.5 border-shield-navy flex items-center justify-center font-bold text-shield-navy text-sm shrink-0">✓</span>
              <span class="font-body font-semibold text-shield-navy text-sm">Laptops and devices</span>
            </li>
            <li class="flex items-start gap-3 bg-shield-ice/40 border-2 border-shield-navy p-3 shadow-brutal-sm">
              <span class="w-6 h-6 bg-[#FFB800] border-1.5 border-shield-navy flex items-center justify-center font-bold text-shield-navy text-sm shrink-0">✓</span>
              <span class="font-body font-semibold text-shield-navy text-sm">Internet connectivity</span>
            </li>
            <li class="flex items-start gap-3 bg-shield-ice/40 border-2 border-shield-navy p-3 shadow-brutal-sm">
              <span class="w-6 h-6 bg-[#FFB800] border-1.5 border-shield-navy flex items-center justify-center font-bold text-shield-navy text-sm shrink-0">✓</span>
              <span class="font-body font-semibold text-shield-navy text-sm">Meals and refreshments</span>
            </li>
            <li class="flex items-start gap-3 bg-shield-ice/40 border-2 border-shield-navy p-3 shadow-brutal-sm">
              <span class="w-6 h-6 bg-[#FFB800] border-1.5 border-shield-navy flex items-center justify-center font-bold text-shield-navy text-sm shrink-0">✓</span>
              <span class="font-body font-semibold text-shield-navy text-sm">Transport support</span>
            </li>
            <li class="flex items-start gap-3 bg-shield-ice/40 border-2 border-shield-navy p-3 shadow-brutal-sm">
              <span class="w-6 h-6 bg-[#FFB800] border-1.5 border-shield-navy flex items-center justify-center font-bold text-shield-navy text-sm shrink-0">✓</span>
              <span class="font-body font-semibold text-shield-navy text-sm">Cloud &amp; software credits</span>
            </li>
            <li class="flex items-start gap-3 bg-shield-ice/40 border-2 border-shield-navy p-3 shadow-brutal-sm">
              <span class="w-6 h-6 bg-[#FFB800] border-1.5 border-shield-navy flex items-center justify-center font-bold text-shield-navy text-sm shrink-0">✓</span>
              <span class="font-body font-semibold text-shield-navy text-sm">Printing &amp; courseware</span>
            </li>
            <li class="flex items-start gap-3 bg-shield-ice/40 border-2 border-shield-navy p-3 shadow-brutal-sm">
              <span class="w-6 h-6 bg-[#FFB800] border-1.5 border-shield-navy flex items-center justify-center font-bold text-shield-navy text-sm shrink-0">✓</span>
              <span class="font-body font-semibold text-shield-navy text-sm">Photography &amp; media</span>
            </li>
          </ul>
        </div>
      </div>

    </div>
  </div>
</section>

<!-- How to Support -->
<section class="py-16 bg-white border-b-2.5 border-shield-navy">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="text-center mb-12">
      <span class="font-mono text-xs font-bold uppercase tracking-widest text-white bg-shield-blue px-3 py-1.5 border-2 border-shield-navy inline-block mb-3 shadow-brutal-sm">
        Get Involved
      </span>
      <h2 class="font-display font-bold text-3xl sm:text-5xl text-shield-navy uppercase tracking-tight">
        Start Supporting Python Weekend Today
      </h2>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-8">

      <div class="bg-white border-2.5 border-shield-navy p-8 shadow-brutal flex flex-col justify-between">
        <div>
          <div class="w-12 h-12 flex items-center justify-center bg-[#FFB800] border-2 border-shield-navy shadow-brutal-sm text-2xl mb-6">📍</div>
          <h3 class="font-display font-bold text-2xl text-shield-navy uppercase tracking-tight mb-4">Sponsor a Local Workshop</h3>
          <p class="font-body text-shield-navy text-base leading-relaxed font-medium mb-8">
            Support a specific Python Weekend edition by contacting its local organising team. Local sponsorship covers venue costs, internet access, participant meals, learning materials, and transport support.
          </p>
        </div>
        <a href="/content/events/" class="btn-brutal-cta">
          <span class="font-display font-bold text-base sm:text-lg text-shield-navy uppercase tracking-wider">View Upcoming Events</span>
        </a>
      </div>

      <div class="bg-white border-2.5 border-shield-navy p-8 shadow-brutal flex flex-col justify-between">
        <div>
          <div class="w-12 h-12 flex items-center justify-center bg-[#FFB800] border-2 border-shield-navy shadow-brutal-sm text-2xl mb-6">🤝</div>
          <h3 class="font-display font-bold text-2xl text-shield-navy uppercase tracking-tight mb-4">Become a Programme Partner</h3>
          <p class="font-body text-shield-navy text-base leading-relaxed font-medium mb-8">
            Companies and institutions can support multiple Python Weekend editions or contribute to resources used across the community — curriculum development, organiser training, website infrastructure, or accessibility.
          </p>
        </div>
        <a href="/contact/" class="btn-brutal-cta">
          <span class="font-display font-bold text-base sm:text-lg text-shield-navy uppercase tracking-wider">Discuss a Partnership</span>
        </a>
      </div>

      <div class="bg-white border-2.5 border-shield-navy p-8 shadow-brutal flex flex-col justify-between">
        <div>
          <div class="w-12 h-12 flex items-center justify-center bg-[#FFB800] border-2 border-shield-navy shadow-brutal-sm text-2xl mb-6">💡</div>
          <h3 class="font-display font-bold text-2xl text-shield-navy uppercase tracking-tight mb-4">Provide In-Kind Support</h3>
          <p class="font-body text-shield-navy text-base leading-relaxed font-medium mb-8">
            Your organisation can contribute venues, devices, internet connectivity, catering, transport vouchers, cloud credits, printing, or technical mentors — directly benefiting learners.
          </p>
        </div>
        <a href="/contact/" class="btn-brutal-cta">
          <span class="font-display font-bold text-base sm:text-lg text-shield-navy uppercase tracking-wider">Contact Us</span>
        </a>
      </div>

    </div>
  </div>
</section>

<!-- Current Work -->
<section class="py-16 bg-shield-ice/20 border-b-2.5 border-shield-navy">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="text-center mb-12">
      <span class="font-mono text-xs font-bold uppercase tracking-widest text-white bg-shield-blue px-3 py-1.5 border-2 border-shield-navy inline-block mb-3 shadow-brutal-sm">
        Community Initiatives
      </span>
      <h2 class="font-display font-bold text-3xl sm:text-5xl text-shield-navy uppercase tracking-tight">
        Current Work That Will Benefit From Your Support
      </h2>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">

      <div class="bg-white border-2.5 border-shield-navy border-t-6 border-t-shield-blue p-6 shadow-brutal">
        <h3 class="font-display font-bold text-xl text-shield-navy uppercase tracking-tight mb-3">Free Local Workshops</h3>
        <p class="font-body text-shield-navy text-sm font-medium leading-relaxed">
          Help local volunteer teams deliver well-organised, beginner-friendly Python and AI workshops without charging participants.
        </p>
      </div>

      <div class="bg-white border-2.5 border-shield-navy border-t-6 border-t-[#FFB800] p-6 shadow-brutal">
        <h3 class="font-display font-bold text-xl text-shield-navy uppercase tracking-tight mb-3">Python and AI Tutorial</h3>
        <p class="font-body text-shield-navy text-sm font-medium leading-relaxed">
          Support the development and maintenance of a clear, practical tutorial that participants can use during workshops and continue using afterwards.
        </p>
      </div>

      <div class="bg-white border-2.5 border-shield-navy border-t-6 border-t-shield-blue p-6 shadow-brutal">
        <h3 class="font-display font-bold text-xl text-shield-navy uppercase tracking-tight mb-3">Organiser &amp; Mentor Guides</h3>
        <p class="font-body text-shield-navy text-sm font-medium leading-relaxed">
          Help us equip local organisers and mentors with guidance that protects programme quality and creates a supportive experience for beginners.
        </p>
      </div>

      <div class="bg-white border-2.5 border-shield-navy border-t-6 border-t-[#FFB800] p-6 shadow-brutal">
        <h3 class="font-display font-bold text-xl text-shield-navy uppercase tracking-tight mb-3">Access &amp; Participation</h3>
        <p class="font-body text-shield-navy text-sm font-medium leading-relaxed">
          Support participants who need access to devices, internet, transport, meals or practical assistance to complete a workshop.
        </p>
      </div>

    </div>
  </div>
</section>"""
        ),
        (
            "/terms/",
            "Terms and Conditions",
            """<section style="background:var(--py-navy);padding:5rem 1.5rem 4rem;text-align:center;">
  <div style="max-width:720px;margin:0 auto;">
    <h1 style="font-family:'Rajdhani',sans-serif;font-size:clamp(2rem,5vw,3rem);font-weight:700;color:var(--py-yellow);margin-bottom:1rem;">Terms and Conditions</h1>
    <p style="font-size:1.05rem;color:rgba(255,255,255,0.75);line-height:1.7;max-width:560px;margin:0 auto;">
      Please read these terms and conditions carefully before using pythonweekend.org.
    </p>
  </div>
</section>

<section class="section-dg">
  <div class="container-dg" style="max-width:820px;">
    <div class="prose prose-dg" style="color:var(--py-body);line-height:1.8;">
      <p>By accessing and using this website, you agree to comply with and be bound by the following terms and conditions of use:</p>
      
      <h2>1. Ownership and Operation</h2>
      <p>pythonweekend.org is owned and operated by Code Campus International. All contents, graphics, and materials associated with Python Weekend are protected under applicable intellectual property laws.</p>
      
      <h2>2. Event Applications and Participant Selection</h2>
      <p>Applications for Python Weekend workshops are submitted through official channels. Submission of an application does not guarantee acceptance or a confirmed workshop seat.</p>
      
      <h2>3. Use of Learning Materials</h2>
      <p>The Python Weekend learning resources, tutorials, and organiser manuals are provided for educational and community use under approved licensing terms.</p>
      
      <h2>4. Code of Conduct</h2>
      <p>All participants, organisers, mentors, and visitors must adhere to the official Python Weekend Code of Conduct across all physical and digital spaces.</p>
      
      <h2>5. Changes and Contact Information</h2>
      <p>We reserve the right to update these terms at any time. For questions regarding terms and conditions, contact us at <strong>hello@pythonweekend.org</strong>.</p>
    </div>
  </div>
</section>"""
        ),
        (
            "/privacy/",
            "Privacy and Cookies Policy",
            """<section style="background:var(--py-navy);padding:5rem 1.5rem 4rem;text-align:center;">
  <div style="max-width:720px;margin:0 auto;">
    <h1 style="font-family:'Rajdhani',sans-serif;font-size:clamp(2rem,5vw,3rem);font-weight:700;color:var(--py-yellow);margin-bottom:1rem;">Privacy and Cookies Policy</h1>
    <p style="font-size:1.05rem;color:rgba(255,255,255,0.75);line-height:1.7;max-width:560px;margin:0 auto;">
      How Python Weekend collects, uses, and protects your personal information.
    </p>
  </div>
</section>

<section class="section-dg">
  <div class="container-dg" style="max-width:820px;">
    <div class="prose prose-dg" style="color:var(--py-body);line-height:1.8;">
      <h2>1. Information We Collect</h2>
      <p>We collect information provided directly by users through event applications, newsletter subscriptions, organiser applications, and contact forms. This may include your name, email address, location, and application responses.</p>
      
      <h2>2. How We Use Information</h2>
      <p>Personal information is used solely to process workshop applications, send newsletter updates, communicate event details, and coordinate local workshops. We do not sell or share user data for commercial advertising.</p>
      
      <h2>3. Cookies and Analytics</h2>
      <p>We use essential cookies to maintain website functionality. Optional analytics cookies may be used to understand how visitors interact with the site to help improve our user experience.</p>
      
      <h2>4. Data Retention and Rights</h2>
      <p>You have the right to request access to, correction of, or deletion of your personal data at any time. To exercise these rights or ask questions about our data practices, email <strong>hello@pythonweekend.org</strong>.</p>
    </div>
  </div>
</section>"""
        )
    ]

    for url, title, content in pages:
        create_or_update_flatpage(url, title, content)

    # Clean up obsolete flatpages from DB
    valid_urls = {url for url, title, content in pages}
    deleted_count, _ = FlatPage.objects.exclude(url__in=valid_urls).delete()
    if deleted_count:
        print(f"Cleaned up {deleted_count} obsolete FlatPages from database.")

if __name__ == "__main__":
    run()

