from django.core.management.base import BaseCommand

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
]

CATEGORIES = {
    'Computing': 'Topics related to computers, software and networks.',
    'Science': 'Natural and formal sciences.',
    'History': 'Events and periods of the past.',
    'Projects': 'Pages about this wiki and its community.',
}


class Command(BaseCommand):
    help = 'Create demo articles and categories for Pedia.'

    def handle(self, *args, **options):
        for name, description in CATEGORIES.items():
            Category.objects.get_or_create(name=name, defaults={'description': description})
            self.stdout.write(f'  category: {name}')

        for data in ARTICLES:
            categories = list(Category.objects.filter(name__in=data['categories']))
            article, created = Article.objects.get_or_create(
                title=data['title'],
                defaults={
                    'content': data['content'],
                    'summary': data['summary'],
                    'is_featured': data['featured'],
                },
            )
            if created:
                article.categories.set(categories)
                article.save_with_revision(summary='Initial version')
                self.stdout.write(self.style.SUCCESS(f'  created: {article.title}'))
            else:
                self.stdout.write(f'  exists:  {article.title}')

        self.stdout.write(self.style.SUCCESS(
            f'Done. {Article.objects.count()} articles, {Category.objects.count()} categories.'
        ))
