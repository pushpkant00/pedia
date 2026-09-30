from django.core.management.base import BaseCommand

from articles import content as content_mod
from articles.models import Article, Category

ARTICLES = [
    {
        'title': 'Pedia',
        'summary': 'A free encyclopedia that anyone can edit.',
        'featured': True,
        'categories': ['Projects'],
        'content': '''
<p><strong>Pedia</strong> is a free, open encyclopedia project built so that anyone can
create and improve articles about any topic. Content is written collaboratively and every
change is recorded in a public revision history.</p>

<h2 id="about-pedia">About</h2>
<p>Every article lives at a permanent address, can be edited by anyone, and can always be
reverted if an edit turns out to be a mistake. See also
<a href="/wiki/python-programming-language/">Python (programming language)</a> and
<a href="/wiki/solar-system/">Solar System</a> for example content.</p>

<h2 id="how-to-contribute">How to contribute</h2>
<ol>
<li>Find a page that needs work — red links point to pages that do not exist yet.</li>
<li>Click <em>Edit</em> and improve the text, add sources, or restructure sections.</li>
<li>Write a short edit summary so other editors know what changed.</li>
</ol>

<h2 id="principles">Core principles</h2>
<ul>
<li><strong>Neutral point of view</strong> — describe disputes fairly.</li>
<li><strong>Verifiability</strong> — claims should be checkable.</li>
<li><strong>No original research</strong> — summarise what is already published.</li>
</ul>

<h2 id="structure">How an article is structured</h2>
<table>
<tr><th>Part</th><th>Purpose</th></tr>
<tr><td>Lead</td><td>Defines the topic in the first paragraph.</td></tr>
<tr><td>Body sections</td><td>Break the topic into subtopics with headings.</td></tr>
<tr><td>Categories</td><td>Place the article in topic indexes at the bottom.</td></tr>
</table>

<blockquote><p>This is a demonstration article. Edit it, or write your own!</p></blockquote>
''',
    },
    {
        'title': 'Python (programming language)',
        'summary': 'High-level, general-purpose programming language created by Guido van Rossum.',
        'featured': True,
        'categories': ['Computing'],
        'content': '''
<p><strong>Python</strong> is a high-level, general-purpose programming language. Its design
philosophy emphasises code readability with the use of significant indentation. Python is
garbage-collected and supports multiple programming paradigms, chiefly
object-oriented, imperative and functional programming.</p>

<h2 id="history">History</h2>
<p>Python was conceived in the late 1980s by <strong>Guido van Rossum</strong> at
Centrum Wiskunde &amp; Informatica in the Netherlands as a successor to the ABC language.
It was first released in 1991. Python 2.0 was released in 2000, and Python 3.0 in 2008 —
a deliberately incompatible version designed to clean up the language.</p>

<h2 id="features">Features</h2>
<ul>
<li>Dynamic typing and automatic memory management</li>
<li>A large standard library, often called "batteries included"</li>
<li>First-class support for modules and packages</li>
<li>Whitespace significance instead of braces for block structure</li>
</ul>

<h2 id="example">Example code</h2>
<pre><code>def fibonacci(n):
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b

print(list(fibonacci(10)))</code></pre>

<h2 id="usage">Usage</h2>
<p>Python is widely used in web development, data science, machine learning, scientific
computing and automation. See <a href="/wiki/world-wide-web/">World Wide Web</a> for the
network it often serves, and [[Artificial intelligence]] for a growing application area.</p>
''',
    },
    {
        'title': 'Solar System',
        'summary': 'The gravitationally bound system of the Sun and the objects orbiting it.',
        'featured': True,
        'categories': ['Science'],
        'content': '''
<p>The <strong>Solar System</strong> is the gravitationally bound system comprising the
Sun and the objects that orbit it. It formed about 4.6 billion years ago from the
gravitational collapse of a giant interstellar molecular cloud.</p>

<h2 id="sun">The Sun</h2>
<p>The Sun is a G-type main-sequence star that contains about 99.86% of the system's total
mass. It generates energy by nuclear fusion of hydrogen into helium in its core.</p>

<h2 id="planets">Planets</h2>
<p>The system contains eight planets, divided into two groups:</p>
<ol>
<li><strong>Terrestrial planets</strong> — Mercury, Venus, Earth and Mars, mostly rock and metal.</li>
<li><strong>Giant planets</strong> — Jupiter, Saturn, Uranus and Neptune, mostly gas and ice.</li>
</ol>

<table>
<tr><th>Planet</th><th>Diameter (km)</th><th>Moons</th></tr>
<tr><td>Earth</td><td>12,742</td><td>1</td></tr>
<tr><td>Jupiter</td><td>139,820</td><td>95</td></tr>
<tr><td>Saturn</td><td>116,460</td><td>146</td></tr>
</table>

<h2 id="smaller-bodies">Smaller bodies</h2>
<ul>
<li><strong>Asteroids</strong> — mostly found in the belt between Mars and Jupiter.</li>
<li><strong>Comets</strong> — icy bodies that develop tails near the Sun.</li>
<li><strong>Dwarf planets</strong> — including Pluto, Eris and Ceres.</li>
</ul>

<p>Related: [[History of astronomy]] and <a href="/wiki/world-wide-web/">World Wide Web</a>,
which is unrelated but demonstrates internal linking.</p>
''',
    },
    {
        'title': 'World Wide Web',
        'summary': 'Information system of interlinked documents accessed via the Internet.',
        'featured': False,
        'categories': ['Computing', 'History'],
        'content': '''
<p>The <strong>World Wide Web</strong> (<strong>WWW</strong>), commonly known as
<strong>the Web</strong>, is an information system enabling documents and other resources
to be accessed over the Internet. Documents are linked by <em>hyperlinks</em> and are
identified by Uniform Resource Locators (URLs).</p>

<h2 id="history-web">History</h2>
<p>The Web was invented in 1989 by British computer scientist <strong>Tim Berners-Lee</strong>
while working at CERN. He published the first web page on 6 August 1991. Berners-Lee
released the Web to the public royalty-free — a decision that made its explosive growth
possible.</p>

<h2 id="how-it-works">How it works</h2>
<ol>
<li>A browser resolves a domain name through DNS.</li>
<li>It requests a resource from a server using HTTP or HTTPS.</li>
<li>The server returns markup, which the browser renders.</li>
</ol>

<h2 id="web-vs-internet">The Web is not the Internet</h2>
<p>The Internet is the global network of computers; the Web is one service that runs on top
of it. Email, for example, also runs on the Internet but is not part of the Web.</p>

<h2 id="impact-web">Impact</h2>
<p>The Web transformed publishing, commerce and communication, and underpins services from
search engines to this encyclopedia. See <a href="/wiki/python-programming-language/">Python
(programming language)</a> for a language widely used to build web services.</p>
''',
    },
    {
        'title': 'Bridges in Mumbai',
        'slug': 'bridges-in-mumbai',
        'summary': 'Overview of the major bridges, causeways and sea links of Mumbai.',
        'featured': True,
        'categories': ['Mumbai', 'Bridges'],
        'content': '''
<p><strong>Mumbai</strong> (formerly Bombay) is connected by a network of bridges, causeways
and sea links spanning Mahim Bay, Thane Creek and the Arabian Sea. Many of these structures
are landmarks in their own right, carrying hundreds of thousands of vehicles every day.</p>

<h2 id="major-crossings">Major crossings</h2>
<table>
<tr><th>Bridge</th><th>Opened</th><th>Length</th><th>Crosses</th></tr>
<tr><td><a href="/wiki/mahim-causeway/">Mahim Causeway</a></td><td>1845</td><td>about 1 mile</td><td>Mahim Creek</td></tr>
<tr><td><a href="/wiki/vashi-bridge/">Vashi Bridge</a></td><td>1997</td><td>1,837.5 m</td><td>Thane Creek</td></tr>
<tr><td><a href="/wiki/airoli-bridge/">Airoli Bridge</a></td><td>1999</td><td>1.03 km (main structure)</td><td>Thane Creek</td></tr>
<tr><td><a href="/wiki/bandra-worli-sea-link/">Bandra–Worli Sea Link</a></td><td>2009</td><td>5.6 km</td><td>Mahim Bay</td></tr>
<tr><td><a href="/wiki/mumbai-trans-harbour-link/">Mumbai Trans Harbour Link</a></td><td>2024</td><td>18.2 km</td><td>Thane Creek</td></tr>
</table>

<h2 id="historic-crossings">Historic crossings</h2>
<p>The <a href="/wiki/mahim-causeway/">Mahim Causeway</a>, opened in 1845, was the first
permanent road linking the island of Bombay with Salsette. Nearly two centuries later it is
still a busy arterial road. At <a href="/wiki/haji-ali-causeway/">Haji Ali</a>, a narrow
causeway with no railings leads to the dargah on its islet — the walk is cut off by the sea
twice a day at high tide.</p>

<h2 id="thane-creek">Thane Creek crossings</h2>
<p>Thane Creek separates Mumbai from Navi Mumbai and is crossed by several road and rail
bridges. The <a href="/wiki/vashi-bridge/">Vashi Bridge</a> (1997) was for decades the main
road entry from the east, followed by the <a href="/wiki/airoli-bridge/">Airoli Bridge</a>
(1999). In 2024 the <a href="/wiki/mumbai-trans-harbour-link/">Mumbai Trans Harbour Link</a>
opened, a 18.2 km sea bridge that is now the longest in India.</p>

<h2 id="sea-links">Sea links</h2>
<p>On the western coast, the <a href="/wiki/bandra-worli-sea-link/">Bandra–Worli Sea Link</a>
crosses Mahim Bay, dramatically shortening the trip between the western suburbs and South
Mumbai. Several more crossings are proposed or under construction, including the
[[Worli Haji Ali Sea Link|Worli–Haji Ali Sea Link]] and the
[[Versova Bandra Sea Link|Versova–Bandra Sea Link]].</p>

<p>See also [[Bandra Worli Sea Link|Bandra–Worli Sea Link]],
[[Mumbai Trans Harbour Link]] and [[Mahim Causeway]].</p>
''',
    },
    {
        'title': 'Bandra–Worli Sea Link',
        'slug': 'bandra-worli-sea-link',
        'summary': '5.6 km cable-stayed sea bridge linking Bandra and Worli across Mahim Bay in Mumbai.',
        'featured': True,
        'categories': ['Mumbai', 'Bridges'],
        'update': True,
        'content': '''
<table class="infobox">
<tr><th class="infobox-title" colspan="2">Bandra–Worli Sea Link</th></tr>
<tr><th class="infobox-header" colspan="2">Characteristics</th></tr>
<tr><th class="infobox-label">Official name</th><td>Rajiv Gandhi Sea Link</td></tr>
<tr><th class="infobox-label">Type</th><td>Cable-stayed sea bridge</td></tr>
<tr><th class="infobox-label">Crosses</th><td>Mahim Bay</td></tr>
<tr><th class="infobox-label">Locale</th><td>Mumbai, Maharashtra</td></tr>
<tr><th class="infobox-label">Total length</th><td>5.6 km</td></tr>
<tr><th class="infobox-label">Lanes</th><td>8</td></tr>
<tr><th class="infobox-label">Longest span</th><td>250 m (twin spans)</td></tr>
<tr><th class="infobox-label">Height (tallest tower)</th><td>128 m</td></tr>
<tr><th class="infobox-header" colspan="2">History</th></tr>
<tr><th class="infobox-label">Construction</th><td>2000–2009</td></tr>
<tr><th class="infobox-label">Opened</th><td>30 June 2009 (first four lanes)</td></tr>
<tr><th class="infobox-label">Fully opened</th><td>24 March 2010</td></tr>
<tr><th class="infobox-label">Construction cost</th><td>₹16 billion</td></tr>
<tr><th class="infobox-label">Toll (car)</th><td>₹85</td></tr>
<tr><th class="infobox-label">Owner</th><td>Government of Maharashtra (MSRDC)</td></tr>
</table>
<p>The <strong>Bandra–Worli Sea Link</strong>, officially the <strong>Rajiv Gandhi Sea
Link</strong>, is a 5.6 km long, 8-lane cable-stayed bridge that crosses Mahim Bay, linking
Bandra in the western suburbs of Mumbai with Worli in South Mumbai. It was the first
cable-stayed bridge built in open seas in India, and it cut the peak-hour trip between
Bandra and Worli from 20–30 minutes to about 10 minutes. It was the longest sea bridge in
India until the <a href="/wiki/mumbai-trans-harbour-link/">Mumbai Trans Harbour Link</a>
opened in 2024.</p>

<h2 id="history">History</h2>
<p>The crossing was planned as the first phase of the proposed Western Freeway; until it
opened, the 1845 <a href="/wiki/mahim-causeway/">Mahim Causeway</a> was the only road link
between Bandra and Worli. The foundation stone was laid in 1999 and construction began in
2000, with the contract awarded to Hindustan Construction Company (HCC) and project
management led by the UK offices of Dar Al-Handasah. The work was split into five
separately contracted packages — the Love Grove flyover, the Bandra cloverleaf interchange,
the Bandra approach road, the central cable-stayed spans and viaducts, and improvements to
Khan Abdul Ghaffar Khan Road.</p>
<p>The project was originally estimated at ₹6.6 billion and was to be finished in five
years. Numerous public interest litigations delayed it by roughly five years and pushed the
cost to about ₹16 billion, with interest costs alone accounting for some ₹7 billion. The
first four of the eight lanes opened to traffic on 30 June 2009, the final connection was
made on 20 April 2009, and all eight lanes were operational from 24 March 2010. The bridge
was named the Rajiv Gandhi Sea Link, with the name reported on 8 July 2009.</p>

<h2 id="design">Design</h2>
<p>The bridge is 5.6 km long and 2 × 20 m wide, carrying eight lanes (four in each
direction) on twin parallel decks. Its two cable-stayed sections are:</p>
<ul>
<li><strong>Bandra channel</strong> — 600 m between expansion joints with a span arrangement
of 50–250–250–50 m, an inverted "Y" centre tower rising 128 m above pile-cap level and 264
stay cables.</li>
<li><strong>Worli channel</strong> — 250 m between expansion joints with a span arrangement
of 50–50–150–50–50 m, an "I" shaped centre tower 55 m tall and 160 stay cables.</li>
</ul>
<p>The approach viaducts are arranged in 300 m units of six 50 m spans. In all, 604 piles
were driven 6–34 m into the substrate — 120 piles of 2 m diameter under the cable-stayed
bridges and 484 piles of 1.5 m diameter under the viaducts. A precast yard cast 2,342
concrete-steel segments, each weighing 110–140 tonnes.</p>

<h2 id="construction">Construction</h2>
<ul>
<li>Viaducts were built span-by-span using a custom self-launching overhead gantry crane,
while the cable-supported superstructure was erected by the balanced cantilever method.</li>
<li>The firm Doka of Austria supplied automatic climbing shutter formwork for the pylons.</li>
<li>Marine geology was difficult: basalts, volcanic tuffs, breccias, weathered rock and up
to 9 m of marine soil, with the foundation bed exposed at low tide and submerged at high
tide. Main tower foundations used 2 m diameter drilled shafts built in the dry with
cofferdams and a tremie seal.</li>
<li>It was the first infrastructure project in Mumbai to use seismic arresters, allowing it
to withstand earthquakes up to magnitude 7.0.</li>
</ul>

<h2 id="operation">Operation and safety</h2>
<p>The bridge is owned by the Government of Maharashtra and maintained by the Maharashtra
State Road Development Corporation (MSRDC), and is insured by New India Assurance. As of
2018 average daily traffic was about 32,312 vehicles. An intelligent bridge management
system provides CCTV cameras, traffic counters, variable message signs, weather monitoring,
emergency telephones and a fibre-optic control network; vehicles are scanned by mobile
explosive detectors, and the tower pillars are ringed by explosion- and collision-resistant
buoys. The Bandra toll plaza has 16 approach lanes with electronic, smart-card and cash
lanes. Two- and three-wheelers are prohibited.</p>

<h2 id="tolls">Tolls</h2>
<p>Toll rates in force from 1 April 2021 are ₹85 for a car single journey, ₹127.5 return
and ₹212.5 for a day pass; ₹130 / ₹195 / ₹325 for tempos and light commercial vehicles;
and ₹175 / ₹262.5 / ₹437.5 for trucks and buses.</p>

<h2 id="criticism">Criticism</h2>
<p>The delay and cost overrun were criticised in the press, and traffic has repeatedly run
below projections: daily traffic fell from 45,952 vehicles in 2011–12 to 40,808 in 2012–13,
with high tolls, congestion at Pedder Road and the Lalbaug flyover cited as factors. The
Worli end is a bottleneck — most of the 4.7 km main length has four lanes each way, but
about 1.2 km at the Worli end narrows to two lanes, causing southbound backlogs.</p>

<p>The bridge now forms part of Mumbai's Coastal Road, which continues north towards
Kandivali. See also [[Bridges in Mumbai]] and [[Mumbai Trans Harbour Link]].</p>
''',
    },
    {
        'title': 'Mumbai Trans Harbour Link',
        'slug': 'mumbai-trans-harbour-link',
        'summary': '18.2 km sea bridge connecting Sewri in Mumbai with Navi Mumbai — the longest sea bridge in India.',
        'featured': True,
        'categories': ['Mumbai', 'Bridges'],
        'update': True,
        'content': '''
<table class="infobox">
<tr><th class="infobox-title" colspan="2">Mumbai Trans Harbour Link</th></tr>
<tr><th class="infobox-header" colspan="2">Characteristics</th></tr>
<tr><th class="infobox-label">Official name</th><td>Atal Bihari Vajpayee Sewri–Nhava Sheva Atal Setu</td></tr>
<tr><th class="infobox-label">Type</th><td>Sea bridge, expressway</td></tr>
<tr><th class="infobox-label">Crosses</th><td>Thane Creek</td></tr>
<tr><th class="infobox-label">Locale</th><td>Mumbai – Navi Mumbai</td></tr>
<tr><th class="infobox-label">Total length</th><td>18.2 km</td></tr>
<tr><th class="infobox-label">Lanes</th><td>6</td></tr>
<tr><th class="infobox-label">Longest span</th><td>180 m</td></tr>
<tr><th class="infobox-label">Piers in water</th><td>1,089</td></tr>
<tr><th class="infobox-label">Design life</th><td>100+ years</td></tr>
<tr><th class="infobox-header" colspan="2">History</th></tr>
<tr><th class="infobox-label">Construction</th><td>April 2018 – December 2023</td></tr>
<tr><th class="infobox-label">Opened</th><td>12 January 2024</td></tr>
<tr><th class="infobox-label">Construction cost</th><td>₹17,843 crore</td></tr>
<tr><th class="infobox-label">Toll (car)</th><td>₹200 (single), ₹300 (return)</td></tr>
<tr><th class="infobox-label">Owner</th><td>MMRDA</td></tr>
</table>
<p>The <strong>Mumbai Trans Harbour Link</strong> (<strong>MTHL</strong>), officially the
<strong>Atal Bihari Vajpayee Sewri–Nhava Sheva Atal Setu</strong> and colloquially known as
<strong>Atal Setu</strong>, is an 18.2 km, 6-lane expressway bridge connecting Mumbai with
Navi Mumbai across Thane Creek. It is the longest sea bridge in India and the world's 12th
longest sea bridge, with a capacity of 70,000 vehicles a day.</p>

<h2 id="history">History</h2>
<p>The need for a new crossing was identified early: a 1963 transport study for Greater
Bombay proposed a sea link to Uran. From the 1990s the Mumbai Metropolitan Region
Development Authority (MMRDA) studied ways to decongest the city, noting that the six older
Thane Creek crossings were narrow, aged and overloaded. Attempts to build the link in 2004,
2005 and 2008 all failed at the bidding stage, and in 2011 the mandate passed from the
MSRDC to MMRDA.</p>
<p>MMRDA appointed Arup and KPMG for a feasibility study in 2011. The project received
state clearance in October 2012, environmental clearance from the MoEFCC on 23 October 2012
(with 11 conditions, including replanting five times the mangroves destroyed), coastal
regulation zone clearance in July 2013, and finance ministerial approval for viability gap
funding in January 2013. After bidders failed to come forward under a public–private
partnership, MMRDA scrapped the PPP model in August 2013 and switched to an engineering,
procurement and construction (EPC) contract. The Japan International Cooperation Agency
(JICA) agreed in February 2016 to fund 80% of the cost at 1–1.4% interest, formalised on 9
May 2016.</p>
<p>Prime Minister Narendra Modi laid the foundation stone on 24 December 2016. Contracts
were awarded in November 2017, construction began on 24 April 2018, and work was delayed
about eight months by the COVID-19 pandemic. Construction finished in December 2023 and the
bridge was inaugurated by Prime Minister Modi on 12 January 2024, at a total cost of ₹17,843
crore (US$1.9 billion).</p>

<h2 id="design">Design</h2>
<ul>
<li>18.2 km long and 27 m wide, with a longest span of 180 m, plus two emergency lanes,
edge strips, crash barriers and noise barriers on both sides.</li>
<li>Precast segmental concrete-steel viaduct built on 1,089 piers standing in water, in
depths reaching 47 m; clearance height 25 m.</li>
<li>Crosses Thane Creek north of Elephanta Island; design life of more than 100 years.</li>
<li>Engineering design by COWI, PADECO, Dar Al-Handasah and T. Y. Lin International; the
general consultant was a consortium of AECOM, Padeco, Dar Al-Handasah and T. Y. Lin.</li>
<li>Three interchanges: the Sewri Y-interchange, the Shivajinagar (Ulwe) cloverleaf and the
Chirle interchange, plus a connector to the Mumbai–Pune Expressway.</li>
</ul>
<p>The construction was split into three civil packages: package 1 (10.38 km across Thane
Creek and the Sewri interchange) went to a consortium of Larsen &amp; Toubro and IHI
Corporation for ₹7,637.3 crore; package 2 (7.807 km and the Shivaji Nagar interchange) to
Tata Projects and Daewoo E&amp;C for ₹5,612.61 crore; and package 3 (3.613 km of viaducts
at Chirle) to L&amp;T for ₹1,013.79 crore. Package 4, the intelligent transport system,
tolling, lighting and buildings, went to Strabag for ₹427 crore.</p>

<h2 id="environment">Environment</h2>
<p>The route passes the Sewri–Mahul mudflats, an Important Bird Area used by some 150 bird
species and by an estimated 20,000–30,000 lesser and greater flamingos. Conditions attached
to the clearances required noise barriers, silencers on construction equipment, no dredging
or reclamation, consultation with the Bombay Natural History Society over migratory birds,
and at least ₹335 crore spent on an environment management programme. The finished bridge
carries noise and vision barriers, and a bird watching platform.</p>

<h2 id="route">Route</h2>
<p>The bridge begins at Sewri in South Mumbai, linked to the Eastern Freeway, and ends at
Chirle near Nhava Sheva in Uran taluka, where it joins NH-348. A single car journey
typically costs ₹200 in toll. By crossing directly over the harbour, Atal Setu has cut the
road journey between Mumbai and Navi Mumbai to a fraction of the time required via the older
<a href="/wiki/vashi-bridge/">Vashi Bridge</a> and <a href="/wiki/airoli-bridge/">Airoli
Bridge</a> crossings.</p>

<h2 id="tolls">Tolls</h2>
<p>Toll rates are ₹200 single / ₹300 return for a car, ₹320 / ₹480 for a bus, ₹655 / ₹985
for a light commercial vehicle, ₹715 / ₹1,075 for a truck, ₹1,030 / ₹1,545 for a heavy-duty
truck and ₹1,255 / ₹1,885 for an oversized truck.</p>

<p>See also [[Bridges in Mumbai]] and [[Bandra Worli Sea Link|Bandra–Worli Sea Link]].</p>
''',
    },
    {
        'title': 'Vashi Bridge',
        'slug': 'vashi-bridge',
        'summary': 'Road bridge over Thane Creek linking Mankhurd in Mumbai with Vashi in Navi Mumbai.',
        'featured': False,
        'categories': ['Mumbai', 'Bridges'],
        'update': True,
        'content': '''
<table class="infobox">
<tr><th class="infobox-title" colspan="2">Vashi Bridge</th></tr>
<tr><th class="infobox-header" colspan="2">Characteristics</th></tr>
<tr><th class="infobox-label">Also known as</th><td>Thane Creek Bridge (TCB-2)</td></tr>
<tr><th class="infobox-label">Type</th><td>Box girder road bridge</td></tr>
<tr><th class="infobox-label">Crosses</th><td>Thane Creek</td></tr>
<tr><th class="infobox-label">Locale</th><td>Mankhurd – Vashi</td></tr>
<tr><th class="infobox-label">Carries</th><td>Sion–Panvel Highway, 6 lanes</td></tr>
<tr><th class="infobox-label">Total length</th><td>1,837.5 m</td></tr>
<tr><th class="infobox-header" colspan="2">History</th></tr>
<tr><th class="infobox-label">Opened</th><td>1997</td></tr>
<tr><th class="infobox-label">Builder</th><td>U.P. State Bridge Corporation</td></tr>
</table>
<p>The <strong>Vashi Bridge</strong>, also known as the <strong>Thane Creek Bridge</strong>
or the <strong>Second Thane Creek Bridge</strong>, is a road bridge across Thane Creek
connecting the suburb of Mankhurd in Mumbai with Vashi in Navi Mumbai. Opened in 1997, it
carries the Sion–Panvel Highway and is one of the main road entry points into Mumbai.</p>

<h2 id="history">History</h2>
<p>The first Thane Creek Bridge (TCB-1), conceived by the engineer Adi Kanga, opened in 1973.
Corrosion cracks appeared in the prestressed girders within two years, and after extensive
repairs the ageing bridge was eventually closed to traffic; it still stands to the north of
the current bridge. The replacement TCB-2 was proposed in 1987, built by the U.P. State
Bridge Corporation and opened in the 1990s. A separate railway bridge across the creek
opened on 9 May 1992.</p>
<p>A third bridge (TCB-3) was proposed in 2012 to handle growing traffic. Construction began
on 29 October 2020 after environmental clearances and pandemic delays, and both directions
were open to traffic by June 2025.</p>

<h2 id="design">Design</h2>
<p>The Vashi Bridge is a 1,837.5 m long box girder bridge carrying a six-lane dual
carriageway, with an emphasis on durability in its construction and design. It runs parallel
to the closed first Thane Creek Bridge.</p>

<h2 id="route">Route</h2>
<p>The bridge carries the Sion–Panvel Highway over Thane Creek. With the
<a href="/wiki/airoli-bridge/">Airoli Bridge</a> upstream and the
<a href="/wiki/mumbai-trans-harbour-link/">Mumbai Trans Harbour Link</a> further south, it is
one of the four road entries into Mumbai, handling traffic bound for the harbour suburbs
and Navi Mumbai.</p>

<p>See also [[Bridges in Mumbai]].</p>
''',
    },
    {
        'title': 'Airoli Bridge',
        'slug': 'airoli-bridge',
        'summary': 'Bridge over Thane Creek connecting Mulund in Mumbai with Airoli in Navi Mumbai, opened 1999.',
        'featured': False,
        'categories': ['Mumbai', 'Bridges'],
        'update': True,
        'content': '''
<table class="infobox">
<tr><th class="infobox-title" colspan="2">Airoli Bridge</th></tr>
<tr><th class="infobox-header" colspan="2">Characteristics</th></tr>
<tr><th class="infobox-label">Type</th><td>Slab and girder bridge</td></tr>
<tr><th class="infobox-label">Crosses</th><td>Thane Creek</td></tr>
<tr><th class="infobox-label">Locale</th><td>Mulund – Airoli</td></tr>
<tr><th class="infobox-label">Carries</th><td>6 lanes</td></tr>
<tr><th class="infobox-label">Main structure</th><td>1,030 m (19 spans)</td></tr>
<tr><th class="infobox-header" colspan="2">History</th></tr>
<tr><th class="infobox-label">Opened</th><td>1999</td></tr>
<tr><th class="infobox-label">Toll (car)</th><td>₹40</td></tr>
<tr><th class="infobox-label">Builder</th><td>Afcons Infrastructure</td></tr>
</table>
<p>The <strong>Airoli Bridge</strong> crosses Thane Creek between Mulund in Mumbai and
Airoli in Navi Mumbai. Opened in 1999, it was the second road bridge linking Mumbai to Navi
Mumbai after the <a href="/wiki/vashi-bridge/">Vashi Bridge</a>, and it remains one of the
busiest crossings in the Mumbai Metropolitan Region.</p>

<h2 id="history">History</h2>
<p>Construction ran from January 1994 to January 1999. The bridge was built by Afcons
Infrastructure, a company of the Shapoorji Pallonji Group, using 800 box girders. Its
opening spurred the development of the Airoli and Thane–Belapur belt, which has since grown
into a major information technology and business corridor.</p>

<h2 id="design">Design</h2>
<ul>
<li>Slab and girder design: a 1,030 m main structure of nineteen 50 m spans between two
40 m end spans, with approach roads taking the crossing to about 3.85 km.</li>
<li>Six lanes, three in each direction.</li>
<li>Maintained by the Maharashtra State Road Development Corporation (MSRDC).</li>
</ul>

<h2 id="route">Route and tolls</h2>
<p>The bridge links the Thane–Belapur Road with the Eastern Express Highway near the
Goregaon–Mulund Link Road intersection. Toll rates are ₹40 for cars and ₹130 for trucks and
buses; two-wheelers cross free of charge. It is one of the most used bridges in Mumbai,
connecting Mulund with the business hubs of Navi Mumbai.</p>

<p>See also [[Bridges in Mumbai]] and [[Mumbai Trans Harbour Link]], a newer crossing
further south.</p>
''',
    },
    {
        'title': 'Mahim Causeway',
        'slug': 'mahim-causeway',
        'summary': 'Historic 1845 causeway across Mahim Creek connecting Mahim and Bandra in Mumbai.',
        'featured': False,
        'categories': ['Mumbai', 'Bridges'],
        'update': True,
        'content': '''
<table class="infobox">
<tr><th class="infobox-title" colspan="2">Mahim Causeway</th></tr>
<tr><th class="infobox-header" colspan="2">Characteristics</th></tr>
<tr><th class="infobox-label">Type</th><td>Causeway</td></tr>
<tr><th class="infobox-label">Crosses</th><td>Mahim Creek</td></tr>
<tr><th class="infobox-label">Locale</th><td>Mahim – Bandra, Mumbai</td></tr>
<tr><th class="infobox-label">Length</th><td>about 1 mile</td></tr>
<tr><th class="infobox-label">Design</th><td>Captain Cruickshank</td></tr>
<tr><th class="infobox-header" colspan="2">History</th></tr>
<tr><th class="infobox-label">Opened</th><td>8 April 1845</td></tr>
<tr><th class="infobox-label">Funded by</th><td>Lady Avabai Jamsetjee Jejeebhoy</td></tr>
<tr><th class="infobox-label">Toll</th><td>Free (by donation condition)</td></tr>
</table>
<p>The <strong>Mahim Causeway</strong> is a historic road across Mahim Creek linking Mahim
in South Mumbai with Bandra. Opened on 8 April 1845, it was the first permanent land
connection between the island of Bombay and Salsette Island, and it remains an arterial link
between the city and its suburbs as part of the Swami Vivekanand Road – L.J. Road corridor.</p>

<h2 id="background">Background</h2>
<p>Before 1845 the only way across Mahim Creek was by boat. The creek was notorious for
fevers — it was called "white man's grave" — and monsoon crossings were perilous. In 1841,
15 to 20 ferries capsized during a storm, drowning many travellers and making the case for a
fixed crossing urgent. The British East India Company declined to fund the project, and
public subscription efforts failed.</p>

<h2 id="construction">Construction and funding</h2>
<p>Lady Avabai Jamsetjee Jejeebhoy, wife of the philanthropist Sir Jamsetjee Jejeebhoy,
offered to pay for the causeway herself, donating ₹155,800 — the vast majority of its cost —
on one condition: no toll would ever be charged for its use. Construction began in 1843
under Captain Cruickshank of the Engineers and took about 20 months. The causeway, nearly a
mile long with a carriageway some 22 feet wide and a central stone arch spanning 100 feet,
was opened on 8 April 1845 by Governor Sir George Arthur in a procession from Parel to
Mahim. Lady Jejeebhoy later donated a further ₹22,000 for the approach road, Lady
Jamsetjee Road, which opened in 1848.</p>

<h2 id="today">Today</h2>
<p>Carrying roughly 50,000 vehicles a day, the causeway was widened in 1941 and now forms
part of the busy SV Road corridor, with the Mumbai Metro running beneath it. Its
commemorative plaque of 1846 survives on L.J. Road. The much newer
<a href="/wiki/bandra-worli-sea-link/">Bandra–Worli Sea Link</a> crosses the same Mahim Bay
further west and carries the traffic the causeway was built to spare.</p>

<p>See also [[Bridges in Mumbai]].</p>
''',
    },
]

CATEGORIES = {
    'Computing': 'Topics related to computers, software and networks.',
    'Science': 'Natural and formal sciences.',
    'History': 'Events and periods of the past.',
    'Projects': 'Pages about this wiki and its community.',
    'Mumbai': 'Mumbai (formerly Bombay), India\u2019s financial capital on the west coast.',
    'Bridges': 'Bridges, causeways and sea links.',
}


class Command(BaseCommand):
    help = 'Create demo articles and categories for Pedia.'

    def handle(self, *args, **options):
        for name, description in CATEGORIES.items():
            Category.objects.get_or_create(name=name, defaults={'description': description})
            self.stdout.write(f'  category: {name}')

        for data in ARTICLES:
            categories = list(Category.objects.filter(name__in=data['categories']))
            defaults = {
                'content': data['content'],
                'summary': data['summary'],
                'is_featured': data['featured'],
            }
            if data.get('slug'):
                defaults['slug'] = data['slug']
            article, created = Article.objects.get_or_create(
                title=data['title'],
                defaults=defaults,
            )
            if created:
                article.categories.set(categories)
                article.save_with_revision(summary='Initial version')
                self.stdout.write(self.style.SUCCESS(f'  created: {article.title}'))
            elif data.get('update'):
                if article.content != content_mod.process(data['content']) or article.summary != data['summary']:
                    article.content = data['content']
                    article.summary = data['summary']
                    article.is_featured = data['featured']
                    article.categories.set(categories)
                    article.save_with_revision(summary='Expanded article with Wikipedia detail')
                    self.stdout.write(self.style.SUCCESS(f'  updated: {article.title}'))
                else:
                    self.stdout.write(f'  current: {article.title}')
            else:
                self.stdout.write(f'  exists:  {article.title}')

        self.stdout.write(self.style.SUCCESS(
            f'Done. {Article.objects.count()} articles, {Category.objects.count()} categories.'
        ))
