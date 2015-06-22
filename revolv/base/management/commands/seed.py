import datetime
from exceptions import NotImplementedError
from optparse import make_option

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from revolv.base.models import RevolvUserProfile
from revolv.payments.models import Payment
from revolv.project.models import Project
from revolv.revolv_cms.models import RevolvCustomPage, RevolvLinkPage
from wagtail.wagtailcore.models import Page, Site


class SeedSpec(object):
    """
    A seed spec is an object which specifies a chunk of data that will be seeded into the
    database when the seed command is run. This is an abstract class: children of it, for
    example RevolvUserProfileSeedSpec or ProjectSeedSpec, must implement a few methods:

    seed(): seeds the data into the database. This function may be indempotent (that is,
        it may leave the database in the same state after being run the first time and
        the second time), but the actual indempotence is up to the specific subclass of
        SeedSpec.

    clear(): clears the data that was seeded. If there was no data seeded, this function
        should do nothing.
    """

    def seed(self, quiet=False):
        raise NotImplementedError("Abstract SeedSpec class tried to call seed()")

    def clear(self, quiet=False):
        raise NotImplementedError("Abstract SeedSpec class tried to call clear()")


class RevolvUserProfileSeedSpec(SeedSpec):
    """
    The database seed specification for revolv.base.models.RevolvUserProfile.

    Creates three users: one donor, one ambassador, and one administrator. Logins are
    donor/password, ambassador/password, administrator/password respectively.
    """
    usernames_to_clear = ["donor", "ambassador", "administrator"]

    def seed(self, quiet=False):
        RevolvUserProfile.objects.create_user(
            username="donor",
            email="donor@re-volv.org",
            first_name="Joe",
            last_name="Donor",
            password="password"
        )
        RevolvUserProfile.objects.create_user_as_ambassador(
            username="ambassador",
            email="ambassador@re-volv.org",
            first_name="Joe",
            last_name="Ambassador",
            password="password"
        )
        RevolvUserProfile.objects.create_user_as_admin(
            username="administrator",
            email="administrator@re-volv.org",
            first_name="Joe",
            last_name="Admin",
            password="password"
        )

    def clear(self, quiet=False):
        for username in self.usernames_to_clear:
            try:
                user = User.objects.get(username=username)
                RevolvUserProfile.objects.get(user=user).delete()
                user.delete()
            except User.DoesNotExist as e:
                if not quiet:
                    print "[Seed:Warning] Error in %s when trying to clear: %s" % (self.__class__.__name__, str(e))


class ProjectSeedSpec(SeedSpec):
    """
    Database seed specification for revolv.project.models.Project

    Creates 4 projects with various settings: Comoonity Dairy, Community Dance Studio,
    Educathing, and Fire Emblem.

    TODO: Make this spec create projects that mirror the projects that RE-volv has already
    completed.
    """
    studio = {
        "funding_goal": 12000.0,
        "title": "Power Community Dance Studio",
        "tagline": "Dance forever, dance until dawn.",
        "video_url": "https://www.youtube.com/watch?v=fzShzO2pk-E",
        "solar_url": "http://home.solarlog-web.net/1445.html",
        "org_name": "The Community Dance Studio",
        "impact_power": 10.0,
        "actual_energy": 0.0,
        "location": "2415 Bowditch St, Berkeley, CA 94704, United States",
        "location_latitude": 37.8670289,
        "location_longitude": -122.2561597,
        "end_date": datetime.date(2050, 10, 8),
        "cover_photo": "covers/box.jpg",
        "org_start_date": datetime.date(1995, 10, 9),
        "mission_statement": "Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.\r\n",
        "description": "Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.\r\n",
        "org_about": "It is a long established fact that a reader will be distracted by the readable content of a page when looking at its layout. The point of using Lorem Ipsum is that it has a more-or-less normal distribution of letters, as opposed to using 'Content here, content here', making it look like readable English. Many desktop publishing packages and web page editors now use Lorem Ipsum as their default model text, and a search for 'lorem ipsum' will uncover many web sites still in their infancy. Various versions have evolved over the years, sometimes by accident, sometimes on purpose (injected humour and the like).\r\n",
        "internal_rate_return": 7.8
    }
    dairy = {
        "funding_goal": 14000.00,
        "title": "Power for Comoonity Dairy",
        "tagline": "Some say that milk is power.",
        "video_url": "https://www.youtube.com/watch?v=JtA8gqWA6PE",
        "solar_url": "http://home.solarlog-web.net/1445.html",
        "org_name": "Comoonity Dairy",
        "impact_power": 12.0,
        "actual_energy": 0.0,
        "location": "1238 5th Street, Berkeley, CA, United States",
        "location_latitude": 37.87968940000000,
        "location_longitude": -122.30289330000000,
        "end_date": datetime.date(2175, 1, 1),
        "cover_photo": "covers/Dairy-Products-vitamin-D-foods.jpg",
        "org_start_date": datetime.date(1997, 10, 9),
        "mission_statement": "With Paper, Facebook has effectively rebooted its core News Feed product on the iPhone. Although Paper is built largely around the same photos and status updates you get from Facebook's main app, it doesn't feel like something that was merely retrofitted to the phone. It emphasizes large photos and swipe gestures, and lets you add general news sections for when you need a break from your friends. It could easily stand in for the main Facebook experience, even if it doesn't have all the same features.\r\n\r\nFacebook isn't alone. Last week, Google announced Inbox, which is built around Gmail but with a different approach to displaying and handling messages. Instead of showing every email in reverse-chronological order, Inbox intelligently sorts messages into groups like \u201cTravel\u201d and \u201cPurchases,\u201d and in a nod to Dropbox's Mailbox, lets you snooze or pin important emails for later.",
        "description": "With Paper, Facebook has effectively rebooted its core News Feed product on the iPhone. Although Paper is built largely around the same photos and status updates you get from Facebook's main app, it doesn't feel like something that was merely retrofitted to the phone. It emphasizes large photos and swipe gestures, and lets you add general news sections for when you need a break from your friends. It could easily stand in for the main Facebook experience, even if it doesn't have all the same features.\r\n\r\nFacebook isn't alone. Last week, Google announced Inbox, which is built around Gmail but with a different approach to displaying and handling messages. Instead of showing every email in reverse-chronological order, Inbox intelligently sorts messages into groups like \u201cTravel\u201d and \u201cPurchases,\u201d and in a nod to Dropbox's Mailbox, lets you snooze or pin important emails for later.",
        "org_about": "The idea that companies should prioritize phones and tablets over old-school PCs isn't new, and companies like Google claim to have been doing it for years. But what they're finally realizing is that mobile-first means more than just making a finely polished app for touch screens. User behavior isn't the same on phones as it is on PCs, which means the app itself must be fundamentally different.\r\n\r\nMicrosoft's Sway, for instance, throws out most of the robust tools that PowerPoint offers, and instead focuses on letting people throw things together quickly, even on a smartphone. It's sort of like using templates in PowerPoint, except that each slide can adapt to the amount of photos and text you put in it, and will format itself automatically for any screen size.",
        "internal_rate_return": 7.5,
    }
    educathing = {
        "funding_goal": 22000.00,
        "title": "Some Education Thing",
        "tagline": "Our children need to learn.",
        "video_url": "https://www.youtube.com/watch?v=slbco4zHmt8",
        "solar_url": "http://home.solarlog-web.net/1445.html",
        "org_name": "Educathing",
        "actual_energy": 0.0,
        "impact_power": 18.0,
        "location": "School, Oakland, CA, United States",
        "location_latitude": "37.79515640000000",
        "location_longitude": "-122.21575089999999",
        "end_date": datetime.date(2200, 01, 01),
        "cover_photo": "covers/education.jpg",
        "org_start_date": datetime.date(1980, 01, 01),
        "mission_statement": "The Internship, which opens on June 7, finds Vince Vaughn and Owen Wilson playing middle-aged watch salesmen who are dinosaurs when it comes to technology. The guys become Google interns--this is a comedy, so just suspend your disbelief--to learn all they can about the digital world. The aspiring tech experts hope to get jobs at Google when all is said and done, but they must beat out brilliant geeks for the coveted positions. Leaving aside the creative merits of the film (just about every reviewer has called The Internship an unabashed, two-hour ad for Google), it does explore a hypothetically interesting topic--what it\u2019s like to make the grade at the competitive corporate promised land of the Internet age.\r\n",
        "description": "The Internship, which opens on June 7, finds Vince Vaughn and Owen Wilson playing middle-aged watch salesmen who are dinosaurs when it comes to technology. The guys become Google interns--this is a comedy, so just suspend your disbelief--to learn all they can about the digital world. The aspiring tech experts hope to get jobs at Google when all is said and done, but they must beat out brilliant geeks for the coveted positions. Leaving aside the creative merits of the film (just about every reviewer has called The Internship an unabashed, two-hour ad for Google), it does explore a hypothetically interesting topic--what it\u2019s like to make the grade at the competitive corporate promised land of the Internet age.\r\n",
        "org_about": "The environment for interns at Google is healthier than it might be portrayed in the movie Ewing says with a laugh, noting, \u201cOne of the biggest differences between the movie and a real internship at Google is that interns are not competing against each other, not for jobs or anything else. We would never pit them against each other.\u201d\r\n\r\nIn addition to working in what Ewing describes as a supportive and collaborative environment, Google interns enjoy competitive pay and perks, and interning can indeed be a path to a full-time job.",
        "internal_rate_return": 7.2,
    }
    emblem = {
        "funding_goal": 24000.00,
        "title": "Roy's our Boy!",
        "tagline": "The force is strong with this boy.",
        "video_url": "https://www.youtube.com/watch?v=I7WqXwb4GQg",
        "solar_url": "http://home.solarlog-web.net/1445.html",
        "org_name": "Fire Emblem",
        "actual_energy": 0.0,
        "impact_power": 18.0,
        "location": "140 New Montgomery, San Francisco, CA, United States",
        "location_latitude": "37.79515640000000",
        "location_longitude": "-122.21575089999999",
        "end_date": datetime.date(2200, 01, 01),
        "cover_photo": "covers/education.jpg",
        "org_start_date": datetime.date(1980, 01, 01),
        "mission_statement": "Fire Emblem, the best game ever.",
        "description": "Fire Emblem, the best game ever.",
        "org_about": "Embark with our heroes on a quest to save the world!",
        "internal_rate_return": 7.0,
    }
    projects_to_clear = [studio, dairy, educathing, emblem]

    def seed(self, quiet=False):
        ambassador = RevolvUserProfile.objects.get(user__username="ambassador")
        Project.factories.active.create(ambassador=ambassador, **self.studio)
        Project.factories.completed.create(ambassador=ambassador, **self.dairy)
        Project.factories.proposed.create(ambassador=ambassador, **self.educathing)
        Project.factories.drafted.create(ambassador=ambassador, **self.emblem)

    def clear(self, quiet=False):
        for project in self.projects_to_clear:
            try:
                Project.objects.get(tagline=project["tagline"]).delete()
            except Project.DoesNotExist as e:
                if not quiet:
                    print "[Seed:Warning] Error in %s when trying to clear: %s" % (self.__class__.__name__, str(e))


class PaymentSeedSpec(SeedSpec):
    """
    Database seed specification for revolv.payments.models.Payment.

    Makes 6 dummy payments. For details, see the seed() method.
    """

    def seed(self, quiet=False):
        donor = RevolvUserProfile.objects.get(user__username="donor")
        ambassador = RevolvUserProfile.objects.get(user__username="ambassador")
        administrator = RevolvUserProfile.objects.get(user__username="administrator")
        studio = Project.objects.get(tagline=ProjectSeedSpec.studio["tagline"])
        dairy = Project.objects.get(tagline=ProjectSeedSpec.dairy["tagline"])

        Payment.factories.base.create(project=studio, user=donor, entrant=donor, amount=50.0)
        Payment.factories.base.create(project=dairy, user=donor, entrant=administrator, amount=50.0)
        Payment.factories.base.create(project=studio, user=donor, entrant=administrator, amount=50.0)
        Payment.factories.base.create(project=studio, user=donor, entrant=administrator, amount=50.0)
        Payment.factories.base.create(project=dairy, user=administrator, entrant=administrator, amount=50.0)
        Payment.factories.base.create(project=studio, user=ambassador, entrant=ambassador, amount=50.0)

    def clear(self, quiet=False):
        try:
            donor = RevolvUserProfile.objects.get(user__username="donor")
            ambassador = RevolvUserProfile.objects.get(user__username="ambassador")
            administrator = RevolvUserProfile.objects.get(user__username="administrator")
            Payment.objects.payments(user=donor).delete()
            Payment.objects.payments(user=ambassador).delete()
            Payment.objects.payments(user=administrator).delete()
        except RevolvUserProfile.DoesNotExist as e:
            if not quiet:
                print "[Seed:Warning] Error in %s when trying to clear: %s" % (self.__class__.__name__, str(e))


class CMSPageSeedSpec(SeedSpec):
    """
    Database seed specification for Wagtail CMS pages. Creates a bunch of
    RevolvCustomPages and RevolvLinkPages that comprise the nav and footer
    menus for the RE-volv app (or at least, the pages that did when this
    spec was written). You can see the page hierarchy in the page_hierarchy,
    where one page is represented by a tuple of <type (link or page)>, <title>,
    and <data (either children or href, depending on type)>.

    At this time, there's no easy one-liner for publishing a wagtail page
    programatically, so this class contains a few helper functions to publish
    pages and also to recursively traverse page_hierarchy so as to keep this code
    as DRY as possible.
    """
    page_hierarchy = [
        ("page", "About Us", [
            ("link", "Our Mission", "/about-us/"),
            ("page", "Our Team", []),
            ("page", "Partners", []),
            ("page", "Jobs", []),
        ]),
        ("page", "What We Do", [
            ("page", "How It Works", []),
            ("page", "Projects", []),
            ("link", "Solar In Your Community", "/what-we-do/"),
        ]),
        ("page", "Get Involved", [
            ("link", "Donate to the Solar Seed Fund", "/get-involved/"),
            ("page", "Solar Ambassador Program", []),
            ("page", "Support Us", []),
            ("page", "Join Our Mailing List", []),
            ("page", "Volunteer", []),
        ]),
        ("page", "Solar Education", [
            ("link", "Educational Resources", "/solar-education/"),
            ("page", "Solar Education Week", []),
        ]),
        ("page", "Media", [
            ("link", "Blog", "/media/"),
            ("page", "Press Room", []),
            ("page", "RE-volv in the News", []),
        ]),
        ("page", "Contact", [
            ("link", "Contact Us", "/contact/"),
        ]),
    ]

    def publish_page_for_parent(self, page, parent, user):
        """
        Publish a wagtail Page (or one of its subclasses, like RevolvCustomPage
        or RevolvLinkPage, as the given user as a child of the given parent.

        Note that the parent passed to this function may be None: if so, then the
        page will be published as a child of the root page of the site. Note that
        there is only one Site object that we care about here, since the RE-volv
        app doesn't have a notion of multiple "sites" to publish pages on - there's
        only one. If for some reason we needed more than one "site", then we would
        need to heavily modify this code.

        References:
            wagtail Site: https://github.com/torchbox/wagtail/blob/e937d7a1a32052966b6dfa9768168ea990f7916a/wagtail/wagtailcore/models.py#L52
            publishing a wagtail page: https://github.com/torchbox/wagtail/blob/e937d7a1a32052966b6dfa9768168ea990f7916a/wagtail/wagtailadmin/views/pages.py#L122
        """
        if parent:
            page_parent = parent
        else:
            only_site = Site.objects.all()[0]
            page_parent = only_site.root_page
        # this actually saves the page
        page_parent.add_child(instance=page)
        page.save_revision(user=user, submitted_for_moderation=False).publish()
        return page

    def publish_page(self, title, body, user, parent=None):
        """
        Publish a RevolvCustomPage with the given title and body, as the given
        user, under the given parent Page. If parent is None, publish under the
        root page of the site instead.
        """
        page = RevolvCustomPage(
            title=title,
            body=body,
            slug=title.lower().replace(" ", "-"),
            seo_title=title,
            show_in_menus=True,
            live=True
        )
        return self.publish_page_for_parent(page, parent, user)

    def publish_link_page(self, title, link_href, user, parent=None):
        """
        Publish a RevolvLinkPage with the given title and href, as the given
        user, under the given parent Page. If parent is None, publish under the
        root page of the site instead.
        """
        page = RevolvLinkPage(
            title=title,
            link_href=link_href,
            slug=title.lower().replace(" ", "-"),
            seo_title=title,
            show_in_menus=True,
            live=True
        )
        return self.publish_page_for_parent(page, parent, user)

    def recursively_seed_pages(self, pages, user, parent=None):
        """
        Given a list of pages to seed as in self.page_hierarchy, recursively
        publish the pages as the given user, under the given parent. If the
        parent is None, as in the other methods of this class, publish under
        the root page of the site instead.
        """
        for page_tuple in pages:
            page_type, title, data = page_tuple
            if page_type == "link":
                self.publish_link_page(title, data, user, parent)
            else:
                new_page = self.publish_page(title, "This is the body of the page", user, parent)
                self.recursively_seed_pages(data, user, new_page)

    def seed(self, quiet=False):
        """
        Publish all the pages in page_hierarchy as the administrator user.
        Because we have to publish as the administrator, this requires the
        revolvuserprofile seed spec to be run before this in order to succeed.
        """
        user = User.objects.get(username="administrator")
        self.recursively_seed_pages(self.page_hierarchy, user)

    def clear(self, quiet=False):
        """
        Clear all the RevolvCustomPages and RevolvLinkPages and reset the site
        root page. We need to reset the site root page because of how django-treebeard
        works. In order to keep a tree of related models, the parent Pages store
        meta information about their children, including paths.

        This means that we can't actually just delete all the Page models that
        we created in seed(): we instead have to do that AND delete the root page
        and reset it.

        References:
            wagtail Site model: https://github.com/torchbox/wagtail/blob/e937d7a1a32052966b6dfa9768168ea990f7916a/wagtail/wagtailcore/models.py#L52
            treebeard add_root() docs: https://tabo.pe/projects/django-treebeard/docs/1.61/api.html#treebeard.models.Node.add_root
        """
        try:
            only_site = Site.objects.all()[0]
            only_site.root_page.delete()
            new_root_page = Page.add_root(title="RE-volv Main Site Root")
            only_site.root_page = new_root_page
            only_site.save()
        except ObjectDoesNotExist as e:
            if not quiet:
                print "[Seed:Warning] Error in %s when trying to clear: %s" % (self.__class__.__name__, str(e))


SPECS_TO_RUN = (
    ("revolvuserprofile", RevolvUserProfileSeedSpec()),
    ("project", ProjectSeedSpec()),
    ("payment", PaymentSeedSpec()),
    ("cms", CMSPageSeedSpec()),
)


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option(
            "--clear",
            action="store_true",
            dest="clear",
            default=False,
            help="Clear the seeded data instead of seeding it."
        ),
        make_option(
            "-s",
            "--spec",
            action="store",
            type="string",
            dest="spec"
        ),
        make_option(
            "--quiet",
            action="store_true",
            dest="quiet",
            default=False,
            help="Don't print warnings or logging information."
        ),
        make_option(
            "-l", "--list",
            action="store_true",
            dest="list",
            default=False,
            help="Show available seeds and exit."
        ),
    )

    def handle(self, *args, **options):
        """
        This handle function is run when the command "python manage.py seed" is run.

        This command seeds the development database. That is, it creates a bunch of dummy
        database entries that are useful for development, like a user account of each type,
        a few projects with varying levels of donation, etc.

        This function is intended to replace loading data in with fixtures, which can
        sometimes cause problems, especially if the models they're loading have signals
        associated with them. This function fully expects signals to be enabled, and will
        create objects knowing that signals will be run on the creation of some of them.

        Options:
            --spec [spec name]: run only the specified SeedSpec
            --clear: clear the seed data instead of seed it
            --list: list available seed specs and stop.
            --quiet: don't print warnings, info notices, etc. Used mostly for keeping test
                output clean.
        """
        def log(message):
            """Log a message if the --quiet flag was not passed."""
            if not options["quiet"]:
                print message

        if options["list"]:
            log("[Seed:Info] The following seeds are available: ")
            log("[Seed:Info]    " + ", ".join([spec_data[0] for spec_data in SPECS_TO_RUN]))
            log("[Seed:Info] Done.")
            return

        if options["clear"]:
            verb = "Clearing"
        else:
            verb = "Seeding"

        specs_to_run = []
        if options["spec"]:
            spec = dict(SPECS_TO_RUN).get(options["spec"])
            if spec is not None:
                specs_to_run.append(spec)
            else:
                log("[Seed:Warning] Trying to run only spec %s, but it doesn't exist." % options["spec"])
        else:
            specs_to_run.extend([tup[1] for tup in SPECS_TO_RUN])

        log("[Seed:Info] %s objects from %i seed spec(s)..." % (verb, len(specs_to_run)))
        for spec in specs_to_run:
            if options["clear"]:
                spec.clear(quiet=options["quiet"])
            else:
                spec.seed(quiet=options["quiet"])
        log("[Seed:Info] Done!")
