# db.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
import requests

db = SQLAlchemy()

# ----------------------------------------------------
#                 MODEL-KLASSEN
# ----------------------------------------------------
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)  # AdminACC
    is_banned = db.Column(db.Boolean, default=False) # Ban


class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], 
                           render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], 
                             render_kw={"placeholder": "Password"})
    submit = SubmitField("Register")

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(username=username.data).first()
        if existing_user_username:
            raise ValidationError("That username already exists. Please choose a different one.")


class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], 
                           render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], 
                             render_kw={"placeholder": "Password"})
    submit = SubmitField("Login")


class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)


class AnimeGenre(db.Model):
    # M:N-Zwischentabelle zwischen AnimeList und Genre
    anime_id = db.Column(db.Integer, db.ForeignKey('anime_list.anime_id'), primary_key=True)
    genre_id = db.Column(db.Integer, db.ForeignKey('genre.id'), primary_key=True)

class Bookmark(db.Model):
    __tablename__ = 'bookmarks'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    anime_id = db.Column(db.Integer, db.ForeignKey('anime_list.anime_id'), nullable=False)

    # Beziehung zu AnimeList
    anime = db.relationship('AnimeList', backref='bookmark_relationship')




class AnimeList(db.Model):
    __tablename__ = 'anime_list'
    anime_id = db.Column(db.Integer, primary_key=True)
    titel = db.Column(db.String(150), nullable=False,unique =True)
    releasedate = db.Column(db.String, nullable=False)
    score = db.Column(db.Integer, db.CheckConstraint('score >= 0 AND score <= 100'), nullable=False)
    summary = db.Column(db.Text, nullable=False)
    Category = db.Column(db.String(20), nullable=False)
    image_url = db.Column(db.String(255))
    genres = db.relationship('Genre', secondary='anime_genre')

class OfferList(db.Model):
    __tablename__='OfferList'
    offer_id =db.Column(db.Integer,primary_key=True)
    titel = db.Column(db.String(150), db.ForeignKey('anime_list.anime_id'), nullable=False)
    price = db.Column(db.Float,nullable=False)
    Offer_Type = db.Column(db.String(10),nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) #Wird benötigt um zu wissen welcher User das Angebot erstellt hat
 
class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    offer_id = db.Column(db.Integer, db.ForeignKey('offer_list.offer_id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    user = db.relationship('User', backref=db.backref('requests', lazy=True))
    offer = db.relationship('OfferList', backref=db.backref('requests', lazy=True))

def add_initial_anime_data(app):
    # Du weißt schon du hättest das einfach alles auf einen txt file schreiben können und dann in die datenbank injecten i mean fuck it it works -Ömer
    initial_anime = [
            {
			'anime_id': 1,
			'titel': 'Frieren: Beyond Journey’s End',
            'releasedate': 'Sep 29 2023',
            'score': 91,
            'summary': 'The adventure is over but life goes on for an elf mage just beginning to learn what living is all about. Elf mage Frieren and her courageous fellow adventurers have defeated the Demon King and brought peace to the land. But Frieren will long outlive the rest of her former party. How will she come to understand what life means to the people around her? Decades after their victory, the funeral of one her friends confronts Frieren with her own near immortality. Frieren sets out to fulfill the last wishes of her comrades and finds herself beginning a new adventure…',
            'Category': 'Series',
            'genres': ['Adventure', 'Drama', 'Fantasy']
            },
            {
			'anime_id': 2,			
			'titel': 'Gintama: THE VERY FINAL',
            'releasedate': 'Jan 8 2021',
            'score': 91,
            'summary': 'Gintama: THE FINAL is the 3rd and final film adaptation of the remainder of the Silver Soul arc and is the series finale.',
            'Category': 'Movie',
            'genres': ['Action', 'Comedy', 'Drama','Sci-Fi']
            },
            {
			'anime_id': 3,
			'titel': 'ONE PIECE FAN LETTER',
            'releasedate': 'Oct 20 2024',
            'score': 91,
            'summary': 'To commemorate the 25th anniversary of the ONE PIECE TV anime: an animated adaptation of the "ONE PIECE novel: Mugiwara Stories".Two years after the Paramount War, the Straw Hats are about to reunite on the Sabaody Archipelago. At the same time, a girl who is head over heels for Nami is trying to hand a fan letter to her before the group leaves the island.',
            'Category': 'Special',
            'genres': ['Action', 'Adventure', 'Fantasy']
            },
            {
			'anime_id': 4,
			'titel': 'Gintama Season 4',
            'releasedate': 'Apr 8 2015',
            'score': 90,
            'summary': 'Gintoki, Shinpachi, and Kagura return as the fun-loving but broke members of the Yorozuya team! Living in an alternate-reality Edo, where swords are prohibited and alien overlords have conquered Japan, they try to thrive on doing whatever work they can get their hands on. However, Shinpachi and Kagura still haven´t been paid... Does Gin-chan really spend all that cash playing pachinko? Meanwhile, when Gintoki drunkenly staggers home one night, an alien spaceship crashes nearby. A fatally injured crew member emerges from the ship and gives Gintoki a strange, clock-shaped device, warning him that it is incredibly powerful and must be safeguarded. Mistaking it for his alarm clock, Gintoki proceeds to smash the device the next morning and suddenly discovers that the world outside his apartment has come to a standstill. With Kagura and Shinpachi at his side, he sets off to get the device fixed; though, as usual, nothing is ever that simple for the Yorozuya team. Filled with tongue-in-cheek humor and moments of heartfelt emotion, Gintama´s fourth season finds Gintoki and his friends facing both their most hilarious misadventures and most dangerous crises yet.',
            'Category': 'Series',
            'genres': ['Action', 'Comedy', 'Drama', 'Sci-Fi']
            },
            {
			'anime_id': 5,
			'titel': 'Fullmetal Alchemist: Brotherhood',
            'releasedate': 'Apr 5 2009',
            'score': 90,
            'summary': 'Alchemy is bound by this Law of Equivalent Exchange—something the young brothers Edward and Alphonse Elric only realize after attempting human transmutation: the one forbidden act of alchemy. They pay a terrible price for their transgression—Edward loses his left leg, Alphonse his physical body. It is only by the desperate sacrifice of Edward´s right arm that he is able to affix Alphonse´s soul to a suit of armor. Devastated and alone, it is the hope that they would both eventually return to their original bodies that gives Edward the inspiration to obtain metal limbs called "automail" and become a state alchemist, the Fullmetal Alchemist.Three years of searching later, the brothers seek the Philosopher´s Stone, a mythical relic that allows an alchemist to overcome the Law of Equivalent Exchange. Even with military allies Colonel Roy Mustang, Lieutenant Riza Hawkeye, and Lieutenant Colonel Maes Hughes on their side, the brothers find themselves caught up in a nationwide conspiracy that leads them not only to the true nature of the elusive Philosopher´s Stone, but their country´s murky history as well. In between finding a serial killer and racing against time, Edward and Alphonse must ask themselves if what they are doing will make them human again... or take away their humanity.',
            'Category': 'Series',
            'genres': ['Action', 'Adventure', 'Drama', 'Fantasy']
            },
            {
			'anime_id': 6,
			'titel': 'Fruits Basket The Final Season',
            'releasedate': 'Apr 6 2021',
            'score': 89,
            'summary': 'After last season’s revelations, the Soma family moves forward, but the emotional chains that bind them are not easily broken. Unable to admit why she wants the cure, Tohru wrestles with the truth, aware that time is running out for someone close. And a secret still lurks that could break another’s heart. But hope is not lost—a clue to the curse is found. Could their imprisonment’s end be near?',
            'Category': 'Series',
            'genres': ['Action', 'Adventure', 'Martial']
            },
            {
			'anime_id': 7,
			'titel': 'Attack on Titan Season 3 Part 2',
            'releasedate': 'Apr 29 2019',
            'score': 89,
            'summary': 'The battle to retake Wall Maria begins now! With Eren’s new hardening ability, the Scouts are confident they can seal the wall and take back Shiganshina District. If they succeed, Eren can finally unlock the secrets of the basement—and the world. But danger lies in wait as Reiner, Bertholdt, and the Beast Titan have plans of their own. Could this be humanity’s final battle for survival?',
            'Category': 'Series',
            'genres': ['Action', 'Drama', 'Fantasy', 'Mystery']
            },
            {
			'anime_id': 8,
			'titel': 'Kaguya-sama: Love is War -Ultra Romantic-',
            'releasedate': 'Apr 9 2022',
            'score': 89,
            'summary': 'The elite members of Shuchiin Academy´s student council continue their competitive day-to-day antics. Council president Miyuki Shirogane clashes daily against vice-president Kaguya Shinomiya, each fighting tooth and nail to trick the other into confessing their romantic love. Kaguya struggles within the strict confines of her wealthy, uptight family, rebelling against her cold default demeanor as she warms to Shirogane and the rest of her friends. Meanwhile, council treasurer Yuu Ishigami suffers under the weight of his hopeless crush on Tsubame Koyasu, a popular upperclassman who helps to instill a new confidence in him. Miko Iino, the newest student council member, grows closer to the rule-breaking Ishigami while striving to overcome her own authoritarian moral code. As love further blooms at Shuchiin Academy, the student council officers drag their outsider friends into increasingly comedic conflicts.',
            'Category': 'Series',
            'genres': ['Comedy', 'Psychological', 'Romance', 'Slice of Life']
            },
            {
			'anime_id': 9,
			'titel': 'Owarimonogatari Second Season',
            'releasedate': 'Aug 12 2017',
            'score': 89,
            'summary': 'Third and “Final Season” of the Monogatari Series, part 4/5. Contains the arcs Mayoi Hell, Hitagi Rendezvous, and Ougi Dark from the Owarimonogatari light novels. Koyomi wakes up to see Mayoi Hachikuji before him, the girl who supposedly had gone to the afterlife. She tells Koyomi that they are currently in Avichi, the lowest levels of hell. Koyomi is dubious of how Mayoi knew about the exact timing of his death and which hell he would drop into, when Mayoi tells him that she was there to pick him up by the request of a certain individual.',
            'Category': 'Series',
            'genres': ['Comedy', 'Mystery', 'Psychological', 'Romance', 'Supernatural']
            },
            {
			'anime_id': 10,
			'titel': 'Hunter x Hunter (2011)',
            'releasedate': 'Oct 2 2011',
            'score': 89,
            'summary': 'A new adaption of the manga of the same name by Togashi Yoshihiro. A Hunter is one who travels the world doing all sorts of dangerous tasks. From capturing criminals to searching deep within uncharted lands for any lost treasures. Gon is a young boy whose father disappeared long ago, being a Hunter. He believes if he could also follow his father´s path, he could one day reunite with him. After becoming 12, Gon leaves his home and takes on the task of entering the Hunter exam, notorious for its low success rate and high probability of death to become an official Hunter. He befriends the revenge-driven Kurapika, the doctor-to-be Leorio and the rebellious ex-assassin Killua in the exam, with their friendship prevailing throughout the many trials and threats they come upon taking on the dangerous career of a Hunter.',
            'Category': 'Series',
            'genres': ['Action', 'Adventure', 'Fantasy']
            },
            {
			'anime_id': 11,
			'titel': 'Steins;Gate',
            'releasedate': 'Apr 6 2011',
            'score': 89,
            'summary': 'Self-proclaimed mad scientist Okabe Rintarou lives in a small room in Akihabara, where he invents "future gadgets" with fellow lab members Shiina Mayuri, his air-headed childhood friend, and Hashida Itaru, an otaku hacker. The three pass the time by tinkering with their latest creation, a "Phone Microwave" that can be controlled through text messages. The lab members soon face a string of mysterious incidents that lead to a game-changing discovery: the Phone Microwave can send emails to the past and thus alter history. Adapted from the critically acclaimed visual novel by 5pb. and Nitroplus, Steins;Gate takes Okabe to the depths of scientific theory and human despair as he faces the dire consequences of changing the past.',
            'Category': 'Series',
            'genres': ['Drama', 'Psychological', 'Sci-Fi', 'Thriller']
            },
            {
			'anime_id': 12,
			'titel': 'March comes in like a lion Season 2',
            'releasedate': 'Oct 14 2017',
            'score': 89,
            'summary': 'The second season of 3-gatsu no Lion. Now in his second year of high school, Rei Kiriyama continues pushing through his struggles in the professional shogi world as well as his personal life. Surrounded by vibrant personalities at the shogi hall, the school club, and in the local community, his solitary shell slowly begins to crack. Among them are the three Kawamoto sisters—Akari, Hinata, and Momo—who forge an affectionate and familial bond with Rei. Through these ties, he realizes that everyone is burdened by their own emotional hardships and begins learning how to rely on others while supporting them in return. Nonetheless, the life of a professional is not easy. Between tournaments, championships, and title matches, the pressure mounts as Rei advances through the ranks and encounters incredibly skilled opponents. As he manages his relationships with those who have grown close to him, the shogi player continues to search for the reason he plays the game that defines his career.',
            'Category': 'Series',
            'genres': ['Drama', 'Slice of Life']
            },
            {
			'anime_id': 13,
			'titel': 'Gintama Season 3',
            'releasedate': 'Oct 4 2012',
            'score': 89,
            'summary': 'While Gintoki Sakata was away, the Yorozuya found themselves a new leader: Kintoki, Gintoki´s golden-haired doppelganger. In order to regain his former position, Gintoki will need the help of those around him, a troubling feat when no one can remember him! Between Kintoki and Gintoki, who will claim the throne as the main character? In addition, Yorozuya make a trip back down to red-light district of Yoshiwara to aid an elderly courtesan in her search for her long-lost lover. Although the district is no longer in chains beneath the earth´s surface, the trio soon learn of the tragic backstories of Yoshiwara´s inhabitants that still haunt them. With flashback after flashback, this quest has Yorozuya witnessing everlasting love and protecting it as best they can with their hearts and souls. Gintama´f: Enchousen includes moments of action-packed intensity along with their usual lighthearted, slapstick humor for Gintoki and his friends.',
            'Category': 'Series',
            'genres': ['Action', 'Comedy', 'Drama', 'Sci-Fi']
            },
            {
			'anime_id': 14,
			'titel': 'Gintama Season 2',
            'releasedate': 'Apr 4 2011',
            'score': 89,
            'summary': 'After a one-year hiatus, Shinpachi Shimura returns to Edo, only to stumble upon a shocking surprise: Gintoki and Kagura, his fellow Yorozuya members, have become completely different characters! Fleeing from the Yorozuya headquarters in confusion, Shinpachi finds that all the denizens of Edo have undergone impossibly extreme changes, in both appearance and personality. Most unbelievably, his sister Otae has married the Shinsengumi chief and shameless stalker Isao Kondou and is pregnant with their first child. Bewildered, Shinpachi agrees to join the Shinsengumi at Otae and Kondou´s request and finds even more startling transformations afoot both in and out of the ranks of the the organization. However, discovering that Vice Chief Toushirou Hijikata has remained unchanged, Shinpachi and his unlikely Shinsengumi ally set out to return the city of Edo to how they remember it. With even more dirty jokes, tongue-in-cheek parodies, and shameless references, Gintama´ follows the Yorozuya team through more of their misadventures in the vibrant, alien-filled world of Edo.',
            'Category': 'Series',
            'genres': ['Action', 'Comedy', 'Drama', 'Sci-Fi']
            },
            {
			'anime_id': 15,
			'titel': 'BLEACH: Thousand-Year Blood War',
            'releasedate': 'Oct 11 2022',
            'score': 88,
            'summary': 'Was it all just a coincidence, or was it inevitable? Ichigo Kurosaki gained the powers of a Soul Reaper through a chance encounter. As a Substitute Soul Reaper, Ichigo became caught in the turmoil of the Soul Society, a place where deceased souls gather. But with help from his friends, Ichigo overcame every challenge to become even stronger. When new Soul Reapers and a new enemy appear in his hometown of Karakura, Ichigo jumps back into the battlefield with his Zanpakuto to help those in need. Meanwhile, the Soul Society is observing a sudden surge in the number of Hollows being destroyed in the World of the Living. They also receive separate reports of residents in the Rukon District having gone missing. Finally, the Seireitei, home of the Soul Reapers, comes under attack by a group calling themselves the Wandenreich. Led by Yhwach, the father of all Quincies, the Wandenreich declare war against the Soul Reapers with the following message: "Five days from now, the Soul Society will be annihilated by the Wandenreich." The history and truth kept hidden by the Soul Reapers for a thousand long years is finally brought to light. All things must come to an end as Ichigo Kurosaki´s final battle begins!',
            'Category': 'Series',
            'genres': ['Action', 'Adventure', 'Supernatural']
            },
            {
			'anime_id': 16,
			'titel': 'Gintama Season 5',
            'releasedate': 'Jan 9 2017',
            'score': 88,
            'summary': 'After joining the resistance against the bakufu, Gintoki and the gang are in hiding, along with Katsura and his Joui rebels. The Yorozuya is soon approached by Nobume Imai and two members of the Kiheitai, who explain that the Harusame pirates have turned against 7th Division Captain Kamui and their former ally Takasugi. The Kiheitai present Gintoki with a job: find Takasugi, who has been missing since his ship was ambushed in a Harusame raid. Nobume also makes a stunning revelation regarding the Tendoushuu, a secret organization pulling the strings of numerous factions, and their leader Utsuro, the shadowy figure with an uncanny resemblance to Gintoki´s former teacher. Hitching a ride on Sakamoto´s space ship, the Yorozuya and Katsura set out for Rakuyou, Kagura´s home planet, where the various factions have gathered and tensions are brewing. Long-held grudges, political infighting, and the Tendoushuu´s sinister overarching plan finally culminate into a massive, decisive battle on Rakuyou.',
            'Category': 'Series',
            'genres': ['Action', 'Comedy', 'Drama', 'Sci-Fi']
            },
            {
			'anime_id': 17,
			'titel': 'Tomorrow´s Joe 2',
            'releasedate': 'Oct 13 1980',
            'score': 88,
            'summary': 'Yabuki Joe is left downhearted and hopeless after a certain tragic event. In attempt to put the past behind him, Joe leaves the gym behind and begins wandering. On his travels he comes across the likes of Wolf Kanagushi and Goromaki Gondo, men who unintentionally fan the dying embers inside him, leading him to putting his wanderings to an end. His return home puts Joe back on the path to boxing, but unknown to himself and his trainer, he now suffers deep-set issues holding him back from fighting. In attempt to quell those issues, Carlos Rivera, a world renowned boxer is invited from Venezuela to help Joe recover.',
            'Category': 'Series',
            'genres': ['Action', 'Drama', 'Slice of Life', 'Sports']
            },
            {
			'anime_id': 18,
			'titel': 'Legend of the Galactic Heroes',
            'releasedate': 'Jan 8 1988',
            'score': 88,
            'summary': 'For decades, the Galactic Empire has been locked in an interstellar war with the Free Planets Alliance, a conflict that involves thousands of spaceships and millions of soldiers on both sides. Two new commanders enter the conflict with great hopes: Imperial Admiral Reinhard von Lohengramm and the FPA´s Yang Wen-Li. As they deal with superiors and subordinates, maneuver through complicated political arrangements, plot strategies, and win battles, each will be tested, and ultimately, changed, by the reality of war.',
            'Category': 'OVA',
            'genres': ['Drama', 'Sci-Fi']
            },
            {
			'anime_id': 19,
			'titel': 'The Apothecary Diaries',
            'releasedate': 'Oct 22 2023',
            'score': 88,
            'summary': 'Maomao lived a peaceful life with her apothecary father. Until one day, she’s sold as a lowly servant to the emperor’s palace. But she wasn’t meant for a compliant life among royalty. So when imperial heirs fall ill, she decides to step in and find a cure! This catches the eye of Jinshi, a handsome palace official who promotes her. Now, she’s making a name for herself solving medical mysteries!',
            'Category': 'Series',
            'genres': ['Drama', 'Mystery']
            },
            {
			'anime_id': 20,
			'titel': 'Vinland Saga Season 2',
            'releasedate': 'Jan 10 2023',
            'score': 88,
            'summary': 'The second season of Vinland Saga. After his father´s death and the destruction of his village at the hands of English raiders, Einar wishes for a peaceful life with his family on their newly rebuilt farms. However, fate has other plans: his village is invaded once again. Einar watches helplessly as the marauding Danes burn his lands and slaughter his family. The invaders capture Einar and take him back to Denmark as a slave. Einar clings to his mother´s final words to survive. He is purchased by Ketil, a kind slave owner and landlord who promises that Einar can regain his freedom in return for working in the fields. Soon, Einar encounters his new partner in farm cultivation—Thorfinn, a dejected and melancholic slave. As Einar and Thorfinn work together toward their freedom, they are haunted by both sins of the past and the ploys of the present. Yet they carry on, grasping for a glimmer of hope, redemption, and peace in a world that is nothing but unjust and unforgiving.',
            'Category': 'Series',
            'genres': ['Action', 'Adventure', 'Drama']
            },
            {
			'anime_id': 21,
			'titel': 'BLEACH: Thousand-Year Blood War - The Conflict',
            'releasedate': 'Oct 5 2024',
            'score': 88,
            'summary': 'The third part of BLEACH: Sennen Kessen-hen.',
            'Category': 'Series',
            'genres': ['Action', 'Adventure', 'Supernatural']
            },
            {
			'anime_id': 22,
			'titel': 'Monster',
            'releasedate': 'Apr 7 2004',
            'score': 88,
            'summary': 'Dr. Kenzo Tenma is a renowned Japanese brain surgeon working at a leading hospital in Germany. One night, Dr. Tenma risks his reputation and career to save the life of a critically wounded young boy over that of the town mayor who had been planning to support the hospital financially. A string of mysterious murders begin to occur soon after the operation, and Dr. Tenma emerges as the primary suspect despite no incriminating evidence. A doctor is taught to believe that all life is equal; however, when another series of murders occur in the surgeon´s vicinity, Dr. Tenma´s beliefs are shaken as his actions that night are shown to have much broader consequences than he could have imagined. Leaving behind his life as a surgeon he embarks on a journey across the country to unravel the mystery of the boy he saved.',
            'Category': 'Series',
            'genres': ['Drama', 'Horror', 'Mystery', 'Psychological', 'Thriller']
            },
            {
			'anime_id': 23,
			'titel': 'A Silent Voice',
            'releasedate': 'Sep 17 2016',
            'score': 88,
            'summary': 'After transferring into a new school, a deaf girl, Shouko Nishimiya, is bullied by the popular Shouya Ishida. As Shouya continues to bully Shouko, the class turns its back on him. Shouko transfers and Shouya grows up as an outcast. Alone and depressed, the regretful Shouya finds Shouko to make amends.',
            'Category': 'Movie',
            'genres': ['Drama', 'Romance', 'Slice of Life']
            },
            {
			'anime_id': 24,
			'titel': 'ONE PIECE',
            'releasedate': 'Oct 20 1999',
            'score': 88,
            'summary': 'Gold Roger was known as the Pirate King, the strongest and most infamous being to have sailed the Grand Line. The capture and death of Roger by the World Government brought a change throughout the world. His last words before his death revealed the location of the greatest treasure in the world, One Piece. It was this revelation that brought about the Grand Age of Pirates, men who dreamed of finding One Piece (which promises an unlimited amount of riches and fame), and quite possibly the most coveted of titles for the person who found it, the title of the Pirate King. Enter Monkey D. Luffy, a 17-year-old boy that defies your standard definition of a pirate. Rather than the popular persona of a wicked, hardened, toothless pirate who ransacks villages for fun, Luffy’s reason for being a pirate is one of pure wonder; the thought of an exciting adventure and meeting new and intriguing people, along with finding One Piece, are his reasons of becoming a pirate. Following in the footsteps of his childhood hero, Luffy and his crew travel across the Grand Line, experiencing crazy adventures, unveiling dark mysteries and battling strong enemies, all in order to reach One Piece.',
            'Category': 'Series',
            'genres': ['Action', 'Adventure', 'Comedy', 'Drama', 'Fantasy']
            },
            {
			'anime_id': 25,
			'titel': 'Mob Psycho 100 II',
            'releasedate': 'Jan 7 2019',
            'score': 88,
            'summary': 'The second season of Mob Psycho 100. Kageyama is an ordinary 8th grader who just wants to live a normal life. Although he can disappear in the crowd in a flash, he was actually the most powerful psychic. The lives of those around Mob and his numerous feelings that softly piles up for the eventual explosion. The mysterious group "Claw" stands before him once again. In the midst of his youthful days, where will his roaring heart take him!?',
            'Category': 'Series',
            'genres': ['Action', 'Comedy', 'Drama', 'Psychological', 'Slice of Life', 'Supernatural']
            },
            {
			'anime_id': 26,
			'titel': 'Monogatari Series Second Season',
            'releasedate': 'Jul 7 2013',
            'score': 88,
            'summary': 'Second season of the Monogatari Series, part 1/2. Contains the arcs Tsubasa Tiger, Mayoi Jiangshi, Nadeko Medusa, Shinobu Time, and Hitagi End, from the Nekomonogatari White, Kabukimonogatari, Otorimonogatari, Onimonogatari and Koimonogatari light novels, respectively.These stories take place after the end of the summer vacation when the apparition of the bee had left and the apparition of the phoenix avoided any consequences… Now that Koyomi Araragi and the girls were entering their new school terms, they were once again about to encounter supernatural beings…but this time, they may not be so easy to deal with. Tsubasa Hanekawa, Mayoi Hachikuji, Nadeko Sengoku, Shinobu Oshino, and finally Hitagi Senjougahara. The girls’ loneliness, their confessions, and their departures… 5 new “stories” begin now.',
            'Category': 'Series',
            'genres': ['Comedy', 'Drama', 'Mystery', 'Psychological', 'Romance', 'Supernatural']
            },
            {
			'anime_id': 27,
			'titel': 'LOOK BACK',
            'releasedate': 'Jun 28 2024',
            'score': 87,
            'summary': 'Ayumu Fujino is a fourth grader who draws a manga strip for the school newspaper. Her art makes her the star of the class, but one day she´s told that Kyomoto, a student who refuses to come to school, would also like to submit a manga for the paper...',
            'Category': 'Movie',
            'genres': ['Drama', 'Slice of Life']
            },
            {
			'anime_id': 28,
			'titel': 'Kaguya-sama: Love is War -The First Kiss That Never Ends-',
            'releasedate': 'Apr 1 2023',
            'score': 87,
            'summary': 'Shuchiin Academy’s student council room: the place where Student Council Vice President Kaguya Shinomiya and President Miyuki Shirogane met. After a long battle in love, these two geniuses communicated their feelings and, at the Hoshin Festival, had their very first kiss. However, there was no clear confession of love. The relationship between these two, who assumed they would be a couple, remains ambiguous. Now, overly conscious of their feelings, they must face the biggest challenge yet: Christmas. It’s Shirogane who wants it to be perfect versus Kaguya who pursues the imperfect situation. This is the very “normal” love story of two geniuses and the first kiss that never ends.',
            'Category': 'Series',
            'genres': ['Comedy', 'Psychological', 'Romance', 'Slice of Life']
            },
            {
			'anime_id': 29,
			'titel': 'JUJUTSU KAISEN Season 2',
            'releasedate': 'Jul 6 2023',
            'score': 87,
            'summary': 'The second season of Jujutsu Kaisen. The past comes to light when second-year students Satoru Gojou and Suguru Getou are tasked with escorting young Riko Amanai to Master Tengen. But when a non-sorcerer user tries to kill them, their mission to protect the Star Plasma Vessel threatens to turn them into bitter enemies and cement their destinies—one as the world’s strongest sorcerer, and the other its most twisted curse user!',
            'Category': 'Series',
            'genres': ['Action', 'Drama', 'Supernatural']
            },
            {
			'anime_id': 30,
			'titel': 'THE FIRST SLAM DUNK',
            'releasedate': 'Dec 3 2022',
            'score': 87,
            'summary': 'Shohoku´s “speedster” and point guard, Ryota Miyagi, always plays with brains and lightning speed, running circles around his opponents while feigning composure. Born and raised in Okinawa, Ryota had a brother who was three years older. Following in the footsteps of his older brother, who was a famous local player from a young age, Ryota also became addicted to basketball. In his second year of high school, Ryota plays with the Shohoku High School basketball team along with Sakuragi, Rukawa, Akagi, and Mitsui as they take the stage at the Inter-High School National Championship. And now, they are on the brink of challenging the reigning champions, Sannoh Kogyo High School.',
            'Category': 'Movie',
            'genres': ['Sports']
            },
            {
			'anime_id': 31,
			'titel': 'Violet Evergarden: the Movie',
            'releasedate': 'Sep 18 2020',
            'score': 87,
            'summary': 'While writing other people’s emotions, she may have neglected her own. Violet Evergarden, the child soldier turned Auto Memory Doll, writes letters that evoke the words her clients can’t. But when a terminally ill boy requests her services for his family, her own feelings about love and loss resurface. Now she must confront her past and the death of the Major.',
            'Category': 'Movie',
            'genres': ['Drama', 'Fantasy', 'Slice of Life']
            },
            {
			'anime_id': 32,
			'titel': 'Gintama.: Silver Soul Arc - Second Half War',
            'releasedate': 'Jul 9 2018',
            'score': 87,
            'summary': 'The second season of the Silver Soul arc.',
            'Category': 'Series',
            'genres': ['Action', 'Comedy', 'Drama', 'Sci-Fi']
            },
            {
			'anime_id': 33,
			'titel': 'Gintama: The Final Chapter - Be Forever Yorozuya',
            'releasedate': 'Jul 6 2013',
            'score': 87,
            'summary': 'When Gintoki apprehends a movie pirate at a premiere, he checks the camera´s footage and finds himself transported to a bleak, post-apocalyptic version of Edo, where a mysterious epidemic called the "White Plague" has ravished the world´s population. It turns out that the movie pirate wasn´t a pirate after all—it was an android time machine, and Gintoki has been hurtled five years into the future! Shinpachi and Kagura, his Yorozuya cohorts, have had a falling out and are now battle-hardened solo vigilantes and he himself has been missing for years, disappearing without a trace after scribbling a strange message in his journal. Setting out in the disguise given to him by the android time machine, Gintoki haphazardly reunites the Yorozuya team to investigate the White Plague, and soon discovers that the key to saving the future lies in the darkness of his own past. Determined to confront a powerful foe, he makes an important discovery—with a ragtag band of friends and allies at his side, he doesn´t have to fight alone.',
            'Category': 'Movie',
            'genres': ['Action', 'Comedy', 'Sci-Fi']
            },
            {
			'anime_id': 34,
			'titel': 'Vinland Saga',
            'releasedate': 'Jul 8 2019',
            'score': 87,
            'summary': 'Thorfinn is son to one of the Vikings greatest warriors, but when his father is killed in battle by the mercenary leader Askeladd, he swears to have his revenge. Thorfinn joins Askeladd´s band in order to challenge him to a duel, and ends up caught in the middle of a war for the crown of England.',
            'Category': 'Series',
            'genres': ['Action', 'Adventure', 'Drama']
            },
            {
			'anime_id': 35,
			'titel': 'Clannad: After Story',
            'releasedate': 'Oct 3 2008',
            'score': 87,
            'summary': 'A few months have passed since Tomoya declared his love to Nagisa, and his life keeps moving forward as he continues to meet a variety of new people, expanding his world in the process. While Tomoya´s world continues to expand, his and Nagisa´s relationship is entering a new phase, and neither of them is quite sure where it will take them. Through his relationship with Nagisa, Tomoya begins to understand the meaning and importance of family. But as Tomoya and Nagisa begin a family of their own, they are faced with many hardships along the way in Clannad: After Story',
            'Category': 'Series',
            'genres': ['Drama', 'Romance', 'Slice of Life', 'Supernatural']
            },
            {
			'anime_id': 36,
			'titel': 'The Dangers in My Heart Season 2',
            'releasedate': 'Jan 7 2024',
            'score': 87,
            'summary': 'The second season of Boku no Kokoro no Yabai Yatsu. After an eventful winter break, Kyoutarou Ichikawa and Anna Yamada reunite with a stronger bond. They continue to grow in their own ways, with Yamada taking on more challenging photoshoots and Ichikawa maturing both physically and emotionally as he tackles his affections for Yamada. However, spending time together outside of school allows for their relationship to deepen, and it becomes increasingly difficult to deny their budding romantic feelings. Grappling with these unexpected and new emotions, Ichikawa and Yamada realize that, with the passage of time, their relationship is bound to change—and they must ultimately decide whether they wish to remain close friends or finally become a couple.',
            'Category': 'Series',
            'genres': ['Comedy', 'Romance', 'Slice of Life']
            },
            {
			'anime_id': 37,
			'titel': 'Sound! Euphonium 3',
            'releasedate': 'Apr 7 2024',
            'score': 87,
            'summary': 'The third season of Hibike! Euphonium. Kumiko´s third year finally begins! With the concert band at Kitauji High School over 90 members, Kumiko is now the president and does her best with her final high school club activities to try to win her long-desired gold at nationals.',
            'Category': 'Series',
            'genres': ['Drama', 'Music', 'Slice of Life']
            },
            {
			'anime_id': 38,
			'titel': 'HAIKYU!! 3rd Season',
            'releasedate': 'Oct 8 2016',
            'score': 87,
            'summary': 'After the victory against Aoba Jousai High, Karasuno High School, once called “a fallen powerhouse, a crow that can’t fly,” has finally reached the climax of the heated Spring tournament. Now, to advance to nationals, the Karasuno team has to defeat the powerhouse Shiratorizawa Academy. Karasuno’s greatest hurdle is their adversary’s ace, Wakatoshi Ushijima, the number one player in the Miyagi Prefecture, and one of the country’s top three aces. Only the strongest team will make it to the national tournament. Since this match is the third-year players’ last chance to qualify for nationals, Karasuno has to use everything they learned during the training camp and prior matches to attain victory. Filled with restlessness and excitement, both teams are determined to come out on top in the third season of Haikyuu!!.',
            'Category': 'Series',
            'genres': ['Comedy', 'Drama', 'Sports']
            },
            {
			'anime_id': 39,
			'titel': 'Kizumonogatari Part 3: Reiketsu',
            'releasedate': 'Jan 6, 2017',
            'score': 87,
            'summary': 'First season of the Monogatari Series, part 4/6. Contains the arc Koyomi Vamp from the Kizumonogatari light novel. With help from Meme Oshino, the apparition specialist, Koyomi defeats the three powerful vampire hunters: Dramaturgy, Episode and Guillotinecutter. Koyomi takes back all the limbs of Kiss-Shot Acerola-Orion Heart-Under-Blade in order to become a human again. But, when he returns to Kiss-Shot, she reveals to him the cold truth of what it means to be a vampire—a creature of the night. Unable to take back what he has done, Koyomi feels nothing but regret and can only deny his dreadful fate. While Koyomi is struggling to face reality, his “friend” Tsubasa Hanekawa comes to him with a certain plan…',
            'Category': 'Movie',
            'genres': ['Action', 'Drama', 'Ecchi', 'Mystery', 'Psychological', 'Supernatural']
            },
            {
			'anime_id': 40,
			'titel': 'Attack on Titan Final Season THE FINAL CHAPTERS Special 1',
            'releasedate': 'Mar 4 2023',
            'score': 87,
            'summary': 'The fate of the world hangs in the balance as Eren unleashes the ultimate power of the Titans. With a burning determination to eliminate all who threaten Eldia, he leads an unstoppable army of Colossal Titans towards Marley. Now a motley crew of his former comrades and enemies scramble to halt his deadly mission, the only question is, can they stop him?',
            'Category': 'Special',
            'genres': ['Action', 'Drama', 'Fantasy', 'Mystery', 'Psychological']
            },
            {
			'anime_id': 41,
			'titel': 'Mob Psycho 100 III',
            'releasedate': 'Oct 6 2022',
            'score': 87,
            'summary': 'The third season of Mob Psycho 100. The appearance of a divine tree and new religion turns Mob and Reigen´s city upside down!',
            'Category': 'Series',
            'genres': ['Action', 'Comedy', 'Drama', 'Psychological', 'Slice of Life', 'Supernatural']
            },
            {
			'anime_id': 42,
			'titel': 'BOCCHI THE ROCK!',
            'releasedate': 'Oct 9 2022',
            'score': 87,
            'summary': 'Hitori Gotou, “Bocchi-chan,” is a girl who’s so introverted and shy around people that she’d always start her conversations with “Ah...” During her middle school years, she started playing the guitar, wanting to join a band because she thought it could be an opportunity for even someone shy like her to also shine. But because she had no friends, she ended up practicing guitar for six hours every day all by herself. After becoming a skilled guitar player, she uploaded videos of herself playing the guitar to the internet under the name “Guitar Hero” and fantasized about performing at her school’s cultural festival concert. But not only could she not find any bandmates, before she knew it, she was in high school and still wasn’t able to make a single friend! She was really close to becoming a shut-in, but one day, Nijika Ijichi, the drummer in Kessoku Band, reached out to her. And because of that, her everyday life started to change little by little...',
            'Category': 'Series',
            'genres': ['Comedy', 'Music', 'Slice of Life']
            },
            {
			'anime_id': 43,
			'titel': 'Revue Starlight: The Movie',
            'releasedate': 'Jun 4 2021',
            'score': 87,
            'summary': 'The stage emulates life and compresses it, setting free skills learned over lifetimes in brief but dazzling displays for the amusement and judgment of others. For the performers, it is the ultimate risk, and some will rise while others must fall. Nowhere is this truer than at the Seisho Music Academy, where music, dance and real weapons all come into play in the creation of the next great Star. Karen and Hikari’s destinies have been linked since a childhood promise, but their journeys here have taken very different paths. Now, after Hikari leaves, Karen must discover who she is without her opposite, while Hikari must rediscover her own course.',
            'Category': 'Movie',
            'genres': ['Action', 'Drama', 'Music', 'Psychological']
            },
            {
			'anime_id': 44,
			'titel': 'MONOGATARI Series: OFF & MONSTER Season',
            'releasedate': 'Jul 6 2024',
            'score': 87,
            'summary': 'The sequel to the Final Season story arc of the Monogatari series. From the past to the future, their story continues. Now that he has graduated from high school, Koyomi Araragi’s story ends here. His story is truly over now, but the stories of the girls Koyomi saved - their stories - are not over yet. This is the prequel or sequel to their stories and their struggles.',
            'Category': 'ONA',
            'genres': ['Drama', 'Mystery', 'Supernatural']
            },
            {
			'anime_id': 45,
			'titel': 'Attack on Titan Final Season THE FINAL CHAPTERS Special 2',
            'releasedate': 'Nov 5 2023',
            'score': 87,
            'summary': 'Eren, as the Founding Titan, advances on Fort Salta with countless other Titans. Appearing before the refugees, who stand on the brink of despair, are Mikasa, Armin, Jean, Conny, Reiner, Pieck, and Levi, who narrowly escaped from the rumbling. The battle between former comrades and childhood friends with Eren concludes here.',
            'Category': 'Special',
            'genres': ['Action', 'Drama', 'Fantasy', 'Psychological', 'Romance']
            },
            {
			'anime_id': 46,
			'titel': 'Code Geass: Lelouch of the Rebellion R2',
            'releasedate': 'Apr 6, 2008',
            'score': 87,
            'summary': 'A year has passed since "The Black Rebellion" and the remaining Black Knights have vanished into the shadows, their leader and figurehead, Zero, executed by the Britannian Empire. Area 11 is once more squirming under the Emperor´s oppressive heel as the Britannian armies concentrate their attacks on the European front. But for the Britannians living in Area 11, life is back to normal. On one such normal day, a Britannian student, skipping his classes in the Ashford Academy, sneaks out to gamble on his chess play. But unknown to this young man, several forces are eying him from the shadows, for soon, he will experience a shocking encounter with his own obscured past, and the masked rebel mastermind Zero will return.',
            'Category': 'Series',
            'genres': ['Action', 'Drama', 'Mecha', 'Sci-Fi', 'Thriller']
            },
            {
			'anime_id': 47,
			'titel': '86 EIGHTY-SIX Part 2',
            'releasedate': 'Oct 3 2021',
            'score': 86,
            'summary': 'The second cour of 86: Eighty Six. Having bid Lena farewell, Shin and the surviving members of the Spearhead squadron continue into the heart of Legion territory. There, they endure countless hardships until they´re rescued by the Federal Republic of Giad, a reformed nation that offers them a second chance at a peaceful life. But it isn´t long before a sense of duty calls the Eighty-Six back to the battlefield. Choosing to enlist in the military, they willingly walk back through the gates of hell, this time joined by a peculiar new ally-Frederica Rosenfort: a haughty young girl with a rare ability and wisdom far beyond her years.',
            'Category': 'Series',
            'genres': ['Action', 'Drama', 'Mecha', 'Sci-Fi']
            },
            {
			'anime_id': 48,
			'titel': 'Hajime no Ippo: The Fighting!',
            'releasedate': 'Oct 4 2000',
            'score': 86,
            'summary': 'Makunouchi Ippo has been bullied his entire life. Constantly running errands and being beaten up by his classmates, Ippo has always dreamed of changing himself, but never has the passion to act upon it. One day, in the midst of yet another bullying, Ippo is saved by Takamura Mamoru, who happens to be a boxer. Ippo faints from his injuries and is brought to the Kamogawa boxing gym to recover. As he regains consciousness, he is awed and amazed at his new surroundings in the gym, though lacks confidence to attempt anything. Takamura places a photo of Ippo´s classmate on a punching bag and forces him to punch it. It is only then that Ippo feels something stir inside him and eventually asks Takamura to train him in boxing. Thinking that Ippo does not have what it takes, Takamura gives him a task deemed impossible and gives him a one week time limit. With a sudden desire to get stronger, for himself and his hard working mother, Ippo trains relentlessly to accomplish the task within the time limit. Thus Ippo´s journey to the top of the boxing world begins.',
            'Category': 'Series',
            'genres': ['Comedy', 'Drama', 'Sports']
            },
            {
			'anime_id': 49,
			'titel': 'HAIKYU!! The Dumpster Battle',
            'releasedate': 'Feb 16 2024',
            'score': 85,
            'summary': 'Theatrical follow-up to Haikyuu!! TO THE TOP 2. The first film of Haikyuu!! FINAL. The Spring Nationals tournament continues on, with Karasuno High matched against rivals Nekoma High, the fated battle between cats versus crows, also known as the highly anticipated “Dumpster Battle”. This match is the long awaited ultimate showdown between two opposing underdog teams.',
            'Category': 'Movie',
            'genres': ['Comedy', 'Drama', 'Sports']
            },
            {
			'anime_id': 50,
			'titel': 'Attack on Titan Final Season',
            'releasedate': 'Dec 7 2020',
            'score': 86,
            'summary': 'It’s been four years since the Scout Regiment reached the shoreline, and the world looks different now. Things are heating up as the fate of the Scout Regiment—and the people of Paradis—are determined at last. However, Eren is missing. Will he reappear before age-old tensions between Marleyans and Eldians result in the war of all wars?',
            'Category': 'Series',
            'genres': ['Action', 'Drama', 'Fantasy', 'Mystery']
            },
            {
			'anime_id': 51,
			'titel': 'Descending Stories: Showa Genroku Rakugo Shinju',
            'releasedate': 'Jan 7 2017',
            'score': 86,
            'summary': 'Unable to forget a performance of "Shinigami" performed by the rakugo master Yakumo in the prison where he was being held, Yotaro´s first act upon his release was go right to the theater, where he begged, pleaded, and was finally accepted as Yakumo´s live-in apprentice. After years of refining his art, Yotaro was promoted to the rank of Shinuchi and inherited the title of 3rd Generation Sukeroku. For the sake of his master Yakumo, Konatsu, and to change the image of Sukeroku inside them both, what kind of rakugo will Yotaro discover? This celebrated human drama, based on a story by Haruko Kumota, offers an honest and sympathetic look into the lives and livelihoods of rakugo storytellers in the Showa era.',
            'Category': 'Series',
            'genres': ['Drama']
            },
            {
			'anime_id': 52,
			'titel': 'MUSHI-SHI The Next Passage 2',
            'releasedate': 'Oct 19 2014',
            'score': 86,
            'summary': 'Second season of Mushishi Zoku Shou. Ghostly, primordial beings known as Mushi continue to cause mysterious changes in the lives of humans. The travelling Mushishi, Ginko, persists in trying to set right the strange and unsettling situations he encounters. Time loops, living shadows, and telepathy are among the overt effects of interference from Mushi, but more subtle symptoms that take years to be noticed also rouse Ginko´s concern as he passes from village to village.',
            'Category': 'Series',
            'genres': ['Adventure', 'Fantasy', 'Mystery', ' Psychological', 'Slice of Life', 'Supernatural']
            },
            {
			'anime_id': 53,
			'titel': 'Link Click Season 2',
            'releasedate': 'Jul 14 2023',
            'score': 86,
            'summary': 'Cheng Xiaoshi by chance meets Lu Guang, a person possessing super powers, and awakens to his own special ability. In order to save the Time Photo Studio which is on the verge of closing down, the two of them start to cooperate in using their super powers to enter photos of customers to complete their commissions. However, the appearance of a mysterious killer shatters the peace, Lu Guang´s condition is still unknown and Qiao Ling has also become entangled in the conspiracy. Faced with all this, how will Cheng Xiaoshi solve the situation?',
            'Category': 'ONA',
            'genres': ['Drama', 'Mystery', 'Supernatural', 'Thriller']
            },
            {
			'anime_id': 54,
			'titel': 'Demon Slayer: Kimetsu no Yaiba Entertainment District Arc',
            'releasedate': 'Dec 5 2021',
            'score': 86,
            'summary': 'After visiting the Rengoku residence, Tanjirou and his comrades volunteer for a mission within the Entertainment District, a place where desires are sold and demons dwell. They journey alongside the flashy Sound Hashira, Tengen Uzui, in search of a monstrous foe terrorizing the town. Sworn to slay creatures of the night, the hunt continues.',
            'Category': 'Series',
            'genres': ['Action', 'Adventure', 'Fantasy', 'Supernatural']
            },
            {
			'anime_id': 55,
			'titel': 'Link Click',
            'releasedate': '2Apr 30 2021',
            'score': 86,
            'summary': 'In a corner of a bustling city, there is a small shop called "Time Photo Studio" operating as usual. Although the entrance looks abandoned, it´s actually run by two men with special abilities: Cheng Xiaoshi and Lu Guang. In order to fulfil customers´ requests, Lu Guang and Cheng Xiaoshi work together and use their special abilities to enter photos. However, things don´t go as planned...',
            'Category': 'ONA',
            'genres': ['Drama', 'Mystery', 'Supernatural', 'Thriller']
            },
            {
			'anime_id': 56,
			'titel': 'Gintama.: Silver Soul Arc',
            'releasedate': 'Jan 8 2018',
            'score': 86,
            'summary': 'Utsuro´s ultimate plan is revealed: spark a universal war that will ultimately lead to the destruction of Earth, allowing him to finally die but taking the universe down with him. Gintoki and others must team up with old allies and former enemies to not only defeat him but also the victims of the immortal´s plans, a gathering army of vengeful Amanto who may no longer listen to reason.',
            'Category': 'Series',
            'genres': ['Action', 'Comedy', 'Drama', 'Sci-Fi']
            },
            {
			'anime_id': 57,
			'titel': 'Attack on Titan Final Season Part 2',
            'releasedate': 'Jan 10 2022',
            'score': 86,
            'summary': 'The war for Paradis zeroes in on Shiganshina just as Jaegerists have seized control. After taking a huge blow from a surprise attack led by Eren, Marley swiftly acts to return the favor. With Zeke’s true plan revealed and a military forced under new rule, this battle might be fought on two fronts. Does Eren intend on fulfilling his half-brother’s wishes or does he have a plan of his own?',
            'Category': 'Series',
            'genres': ['Action', 'Drama', 'Fantasy', 'Mystery', 'Psychological']
            },
            {
			'anime_id': 58,
			'titel': 'BLEACH: Thousand-Year Blood War - The Separation',
            'releasedate': 'Jul 8 2023',
            'score': 86,
            'summary': 'The second part of BLEACH: Sennen Kessen-hen. After a brutal surprise attack by the forces of Quincy King Yhwach, the resident Reapers of the Soul Society lick their wounds and mourn their losses. Many of the surviving Soul Reaper captains train to battle without their Bankai, the ultimate technique wielded by the fiercest warriors. In the previous assault, Ichigo Kurosaki narrowly managed to help fend off Yhwach´s fearsome wrath. However, to ultimately defeat his godly adversary and save his allies, Ichigo must now undergo severe training that will push him beyond his physical, emotional, and mental limits. Though Yhwach already holds the upper hand in this ongoing blood feud, he also successfully recruits Uryuu Ishida, Ichigo´s close friend and rival, to be his successor. Yhwach strikes out once again at the weakened Soul Society, intent on finally obliterating his long-standing enemies. As Ichigo struggles to attain new power, the Soul Reaper captains fight for survival and borrowed time.',
            'Category': 'Series',
            'genres': ['Action', 'Adventure', 'Supernatural']
            },
            {
			'anime_id': 59,
			'titel': 'Oshi no Ko Season 2',
            'releasedate': 'Jul 3 2024',
            'score': 86,
            'summary': 'The second season of [Oshi no Ko]. Aqua’s desire for revenge takes center stage as he navigates the dark underbelly of the entertainment world alongside his twin sister, Ruby. While Ruby follows in their slain mother’s footsteps to become an idol, Aqua joins a famous theater troupe in hopes of uncovering clues to the identity of his father — the man who arranged their mother’s untimely death, and the man who once starred in the same troupe Aqua hopes to infiltrate.',
            'Category': 'Series',
            'genres': ['Drama', 'Mystery', 'Psychological', 'Supernatural']
            },
            {
			'anime_id': 60,
			'titel': 'Re:ZERO -Starting Life in Another World- Season 3',
            'releasedate': 'Oct 2 2024',
            'score': 86,
            'summary': 'The third season of Re:Zero kara Hajimeru Isekai Seikatsu. A year has passed since Subaru’s victory at the Sanctuary. He savors a life of fulfillment while Emilia’s camp stands united for the royal selection—until a fateful letter arrives. Anastasia, a royal selection candidate, has invited Emilia to the Watergate City of Priestella. But as the party begins its journey, crisis stirs beneath the surface and Subaru meets a cruel fate once again.',
            'Category': 'Series',
            'genres': ['Action', 'Adventure', 'Drama', 'Fantasy', 'Psychological', 'Romance', 'Thriller']
            },
            {
			'anime_id': 61,
			'titel': 'HAIKYU!! 2nd Season',
            'releasedate': 'Oct 4, 2015',
            'score': 86,
            'summary': 'Following their participation at the Inter-High, the Karasuno High School volleyball team attempts to refocus their efforts, aiming to conquer the Spring tournament instead. When they receive an invitation from long-standing rival Nekoma High, Karasuno agrees to take part in a large training camp alongside many notable volleyball teams in Tokyo and even some national level players. By playing with some of the toughest teams in Japan, they hope not only to sharpen their skills, but also come up with new attacks that would strengthen them. Moreover, Hinata and Kageyama attempt to devise a more powerful weapon, one that could possibly break the sturdiest of blocks. Facing what may be their last chance at victory before the senior players graduate, the members of Karasuno´s volleyball team must learn to settle their differences and train harder than ever if they hope to overcome formidable opponents old and new—including their archrival Aoba Jousai and its world-class setter Tooru Oikawa.',
            'Category': 'Series',
            'genres': ['Comedy', 'Drama', 'Sports']
            },
            {
			'anime_id': 62,
			'titel': 'MUSHI-SHI The Next Passage',
            'releasedate': 'Jun 21 2014',
            'score': 86,
            'summary': 'They existed long before anyone can remember. They are simple and strange in nature, not resembling any other plant or animal in this world. In ancient times, people revered these bizarre creatures and called them "Mushi." People once again began to believe in the existence of these "Mushi" when they began affecting their lives in inexplicable ways. The one who connects the world of "Mushi" to the world of humans—they were called the "Mushi-shi." All life exists not to hinder others in this world. They are simply there to live as they were meant to.',
            'Category': 'Series',
            'genres': ['Adventure', 'Fantasy', 'Mystery', 'Psychological', 'Slice of Life', 'Supernatural']
            },
            {
			'anime_id': 63,
			'titel': 'ARIA The ORIGINATION',
            'releasedate': 'Jan 8 2008',
            'score': 86,
            'summary': 'In Neo Venezia, Akari, Aika, and Alice continue to work diligently toward the day they become full-fledged Prima Undine (a professional tour guide gondolier). The girls have come far since they began their training, and they are slowly forming their own distinctive styles as tour guides for the city. On the long journey towards their goal, the girls have relied on the advice of their seniors from their respective companies: the patient and understanding Alicia from Aria Company, the strict and proper Akira from Himeya Company, and the clumsy yet caring Athena from Orange Planet Company. Will the girls be able to blend the advice from their mentors with their personally acquired knowledge of Neo Venezia to become praiseworthy Prima Undines? Welcome once more to Neo Venezia; the city that personifies warmth and tranquility.',
            'Category': 'Series',
            'genres': ['Fantasy', 'Sci-Fi', 'Slice of Life']
            },
            {
			'anime_id': 64,
			'titel': 'Cowboy Bebop',
            'releasedate': 'Apr 3 1998',
            'score': 86,
            'summary': 'Enter a world in the distant future, where Bounty Hunters roam the solar system. Spike and Jet, bounty hunting partners, set out on journeys in an ever struggling effort to win bounty rewards to survive. While traveling, they meet up with other very interesting people. Could Faye, the beautiful and ridiculously poor gambler, Edward, the computer genius, and Ein, the engineered dog be a good addition to the group?',
            'Category': 'Series',
            'genres': ['Action', 'Adventure', 'Drama', 'Sci-Fi']
            },
            {
			'anime_id': 65,
			'titel': 'Uma Musume: Pretty Derby - Shin Jidai no Tobira',
            'releasedate': 'May 24 2024',
            'score': 86,
            'summary': 'Jungle Pocket, an Umamusume who has been racing tirelessly in pursuit of becoming the greatest, is ready to take on the once-in-a-lifetime Classic Triple Crown series. However, standing in her way are rivals from the same generation, whose talent may even surpass her own.',
            'Category': 'Movie',
            'genres': ['Drama', 'Slice of Life', 'Sports']
            },
            {
			'anime_id': 66,
			'titel': 'Kaguya-sama: Love is War?',
            'releasedate': 'Apr 11 2020',
            'score': 86,
            'summary': 'After a slow but eventful summer vacation, Shuchiin Academy´s second term is now starting in full force. As August transitions into September, Miyuki Shirogane´s birthday looms ever closer, leaving Kaguya Shinomiya in a serious predicament as to how to celebrate it. Furthermore, the tenure of the school´s 67th student council is coming to an end. Due to the council members being in different classes, the only time Kaguya and Miyuki have to be together will soon disappear, putting all of their cunning plans at risk. A long and difficult election that will decide the fate of the new student council awaits, as multiple challengers fight for the coveted title of president.',
            'Category': 'Series',
            'genres': ['Comedy', 'Psychological', 'Romance', 'Slice of Life']
            },
            {
			'anime_id': 67,
			'titel': 'The Disappearance of Haruhi Suzumiya',
            'releasedate': 'Feb 6 2010',
            'score': 86,
            'summary': 'It is mid-December, and SOS Brigade chief Haruhi Suzumiya announces that the Brigade is going to hold a Christmas party in their clubroom, with Japanese hotpot for dinner. The brigade members Kyon, Yuki Nagato, Mikuru Asahina and Itsuki Koizumi start preparing everything for the party, such as costumes and decorations. But a couple of days later, Kyon arrives at school only to find that Haruhi is missing. Not only that, but Mikuru claims she has never known Kyon before, Koizumi is also missing, and Yuki has become the sole member of the literature club. The SOS Brigade seems to have never existed, nor has Haruhi Suzumiya. No one in the school has ever heard about her... except for Kyon.',
            'Category': 'Movie',
            'genres': ['Drama', 'Mystery', 'Sci-Fi', 'Supernatural']
            },
            {
			'anime_id': 68,
			'titel': 'Spirited Away',
            'releasedate': 'Jul 20 2001',
            'score': 85,
            'summary': 'On the way to their new home, 10-year-old Chihiro Ogino´s family stumbles upon a deserted theme park. Intrigued, the family investigates the park, though unbeknownst to them, it is secretly inhabited by spirits who sleep by day and appear at night. When Chihiro´s mother and father eat food from a restaurant in the street, angry spirits turn them into pigs. Furthermore, a wide sea has appeared between the spirit world and the human one, trapping Chihiro, the sole human, in a land of spirits. Luckily for her though, a mysterious boy named Haku appears, claiming to know her from the past. Under his instructions, Chihiro secures a job in the bathhouse where Haku works. With only her courage and some new found friends to aid her, Chihiro embarks on a journey to turn her parents back to their original forms and return home.',
            'Category': 'Movie',
            'genres': ['Adventure', 'Drama', 'Fantasy', 'Supernatural']
            },
            {
			'anime_id': 69,
			'titel': 'Mushoku Tensei: Jobless Reincarnation Cour 2',
            'releasedate': 'Oct 4 2021',
            'score': 85,
            'summary': 'After the mysterious mana calamity, Rudeus Greyrat and his fierce student Eris Boreas Greyrat are teleported to the Demon Continent. There, they team up with their newfound companion Ruijerd Supardia—the former leader of the Superd´s Warrior group—to form "Dead End," a successful adventurer party. Making a name for themselves, the trio journeys across the continent to make their way back home to Fittoa. Following the advice he received from the faceless god Hitogami, Rudeus saves Kishirika Kishirisu, the Great Emperor of the Demon World, who rewards him by granting him a strange power. Now, as Rudeus masters the powerful ability that offers a number of new opportunities, it might prove to be more than what he bargained for when unexpected dangers threaten to hinder their travels.',
            'Category': 'Series',
            'genres': ['Adventure', 'Drama', 'Ecchi', 'Fantasy']
            },
            {
			'anime_id': 70,
			'titel': 'The Founder of Diabolism: Final Season',
            'releasedate': 'Aug 7 2021',
            'score': 85,
            'summary': 'The third season of Modao Zushi.',
            'Category': 'ONA',
            'genres': ['Action', 'Adventure', 'Drama', 'Fantasy', 'Mystery', 'Supernatural']
            },
            {
			'anime_id': 71,
			'titel': 'Made in Abyss: The Golden City of the Scorching Sun',
            'releasedate': '2002-10-03',
            'score': 85,
            'summary': 'The second season of Made in Abyss. Directly after the events of Made in Abyss: Fukaki Tamashii no Reimei, the third installment of Made in Abyss covers the adventures of Reg, Riko, and Nanachi in the Sixth Layer, The Capital of the Unreturned.',
            'Category': 'Series',
            'genres': ['Adventure', 'Drama', 'Fantasy', 'Horror', 'Mystery', 'Sci-Fi']
            },
            {
			'anime_id': 72,
			'titel': 'Ping Pong the Animation',
            'releasedate': 'Apr 11 2014',
            'score': 85,
            'summary': 'Tsukimoto Makoto (nicknamed Smile) is a quiet high-schooler who´s been friends with the loud and energetic Hoshino Yukata (nicknamed Peko). They´re both in the table tennis club and are very good at it, though Smile´s personality prevents him from winning against Peko. The club teacher however notices Smile´s talent and tries to make him gain some sportive tenacity.',
            'Category': 'Series',
            'genres': ['Drama', 'Psychological', 'Sports']
            },
            {
			'anime_id': 73,
			'titel': 'Bungo Stray Dogs 5',
            'releasedate': 'Jul 12 2023',
            'score': 85,
            'summary': 'The fifth season of Bungou Stray Dogs. Detective employees are caught one after another, and Kamui, the leader of Tenjin Goshui, is closing in on the Armed Detective Agency. Will the Agency survive?!',
            'Category': 'Series',
            'genres': ['Action', 'Comedy', 'Mystery', 'Supernatural']
            },
            {
			'anime_id': 74,
			'titel': 'Made in Abyss: Dawn of the Deep Soul',
            'releasedate': 'Jan 17 2020',
            'score': 85,
            'summary': 'Dawn of the Deep Soul continues the epic adventure of plucky Riko and Reg who are joined by their new friend Nanachi. Together they descend into the Abyss’ treacherous fifth layer, the Sea of Corpses, and encounter the mysterious Bondrewd, a legendary White Whistle whose shadow looms over Nanachi’s troubled past. Bondrewd is ingratiatingly hospitable, but the brave adventurers know things are not always as they seem in the enigmatic Abyss...',
            'Category': 'Movie',
            'genres': ['Action', 'Adventure', 'Drama', 'Fantasy', 'Horror', 'Mystery', 'Psychological', 'Sci-Fi']
            },
            {
			'anime_id': 75,
			'titel': 'Your Name.',
            'releasedate': 'Aug 26, 2016',
            'score': 85,
            'summary': 'Mitsuha Miyamizu, a high school girl, yearns to live the life of a boy in the bustling city of Tokyo—a dream that stands in stark contrast to her present life in the countryside. Meanwhile in the city, Taki Tachibana lives a busy life as a high school student while juggling his part-time job and hopes for a future in architecture. One day, Mitsuha awakens in a room that is not her own and suddenly finds herself living the dream life in Tokyo—but in Taki´s body! Elsewhere, Taki finds himself living Mitsuha´s life in the humble countryside. In pursuit of an answer to this strange phenomenon, they begin to search for one another. Kimi no Na wa. revolves around Mitsuha and Taki´s actions, which begin to have a dramatic impact on each other´s lives, weaving them into a fabric held together by fate and circumstance.',
            'Category': 'Movie',
            'genres': ['Action', 'Adventure', 'Martial']
            },
            {
			'anime_id': 76,
			'titel': 'DAN DA DAN',
            'releasedate': 'Oct 4 2024',
            'score': 85,
            'summary': 'This is a story about Momo, a high school girl who comes from a family of spirit mediums, and her classmate Okarun, an occult fanatic. After Momo rescues Okarun from being bullied, they begin talking. However, an argument ensues between them since Momo believes in ghosts but denies aliens exist, and Okarun believes in aliens but denies ghosts exist. To prove to each other what they believe in is real, Momo goes to an abandoned hospital where a UFO has been spotted and Okarun goes to a tunnel rumored to be haunted. To their surprise, they each encounter overwhelming paranormal activities that transcend comprehension. Amid these predicaments, Momo awakens her hidden power and Okarun gains the power of a curse to overcome these new dangers! Their fateful love begins as well!? The story of the occult battle and adolescence starts!',
            'Category': 'Series',
            'genres': ['Action', 'Comedy', 'Drama', 'Romance', 'Sci-Fi', 'Supernatural']
            },
            {
			'anime_id': 77,
			'titel': 'ODDTAXI',
            'releasedate': 'Apr 6 2021',
            'score': 85,
            'summary': 'The taxi driver Odokawa lives a very mundane life. He has no family, doesn´t really hang out with others, and he´s an oddball who is narrow-minded and doesn´t talk much. The only people he can call his friends are his doctor, Gouriki and his classmate from high school, Kakihana. All of his patrons seem to be slightly odd themselves. The college student who wants the world to notice him online, Kabasawa. A nurse with secrets named Shirakawa. A comedy duo that just can´t catch a break named the Homosapiens. A local hoodlum named Dobu. An idol group that´s just starting out named Mystery Kiss... All these mundane conversations somehow eventually lead to a girl who´s gone missing.',
            'Category': 'Series',
            'genres': ['Drama', 'Mystery', 'Psychological', 'Thriller']
            },
            {
			'anime_id': 78,
			'titel': 'Heaven Official´s Blessing Season 2',
            'releasedate': 'Oct 18 2023',
            'score': 85,
            'summary': 'The second season of Tian Guan Ci Fu.',
            'Category': 'ONA',
            'genres': ['Adventure', 'Drama', 'Fantasy', 'Romance']
            },
            {
			'anime_id': 79,
			'titel': 'Fruits Basket Season 2',
            'releasedate': 'Apr 7 2020',
            'score': 85,
            'summary': 'A year has passed since Tohru Honda began living in the Souma residence, and she has since created stronger relationships with its inhabitants Shigure, Kyou, and Yuki. She has also grown closer to the rest of the Souma family and has become familiar with their ancestral secret, having helped them with many of their personal issues. The closer Tohru gets, however, the more she begins to realize that their secret holds a darker truth than she first presumed. Summer is approaching and Tohru is invited to spend her days with the Soumas, mainly Kyou and Yuki. Tohru wishes for an easy-going vacation, but her close relationships with the two boys and the rest of the Soumas may prove to cause trouble. As they grow more intimate, their carefree time together is hindered by older hardships and feelings from the past that begin to resurface. The Eternal Banquet also dawns on the members of the zodiac, and they must tend to their duties alongside the unnerving head of the family, Akito Souma. With the banquet approaching and a plethora of feelings to be solved, will Tohru´s life with the Soumas remain peaceful, or will she find herself in a situation from which she cannot escape?',
            'Category': 'Series',
            'genres': ['Comedy', 'Drama', 'Psychological', 'Romance', 'Slice of Life', 'Supernatural']
            },
            {
			'anime_id': 80,
			'titel': 'Fate/stay night [Heaven’s Feel] III. spring song',
            'releasedate': 'Aug 15 2020',
            'score': 85,
            'summary': 'The third film in a trilogy adaptation of the 3rd route of the popular visual novel: Fate/stay night. To save the girl, to enact the justice he´s chosen...The young man will no longer turn a blind eye to the truth. Mages (Masters) and Heroic Spirits (Servants) work together in the battles of the Holy Grail War, a fight for an omnipotent wish-granting container called the Holy Grail. However, this war has become horribly twisted. A young woman named Sakura Matou, with the sins she has committed, drowns in the murky darkness. A young man named Shirou Emiya, who vowed to protect Sakura, works together with Rin Tohsaka and throws himself into the raging battle to put a stop to the Holy Grail War. Illyasviel von Einzbern, as one of the few who knows the truth behind the conflict, confronts her own fate, while Zouken Matou uses Sakura to try to fulfill his own desires. Will the young man’s wish reach her even as he challenges fate itself, battling against the rising tide? The Holy Grail War is coming to an end... The final battle is about to begin.',
            'Category': 'Movie',
            'genres': ['Action', 'Drama', 'Fantasy', 'Psychological', 'Supernatural', 'Thriller']
            },
            {
			'anime_id': 81,
			'titel': 'Evangelion: 3.0+1.0 Thrice Upon a Time',
            'releasedate': 'Mar 8 2021',
            'score': 85,
            'summary': 'In the aftermath of the Fourth Impact, stranded without their Evangelions, Shinji, Asuka, and Rei find refuge in one of the rare pockets of humanity that still exist on the ruined planet Earth. There, each of them live a life far different from their days as an Evangelion pilot. However, the danger to the world is far from over. A new impact is looming on the horizon—one that will prove to be the true end of Evangelion. Finally, the Human Instrumentality Project is set in motion, and WILLE makes one last grueling stand to prevent the Final Impact.',
            'Category': 'Movie',
            'genres': ['Action', 'Drama', 'Mecha', 'Psychological', 'Sci-Fi']
            },
            {
			'anime_id': 82,
			'titel': 'Kingdom Season 3',
            'releasedate': 'Apr 6 2020',
            'score': 85,
            'summary': 'The third season of Kingdom. Following the successful Sanyou campaign, the Qin army, including 1,000-Man Commander Xin, inches ever closer to fulfilling King Ying Zheng´s dream of unifying China. With a major geographical foothold in the state of Wei now under its control, Qin sets its sights eastward toward the remaining warring states. Meanwhile Li Mu—an unparalleled strategist and the newly appointed prime minister of the state of Zhao—has taken advantage of Zhao´s temporary truce with Qin to negotiate with the other states without interruption. Seemingly without warning, Ying Zheng receives news that armies from the states of Chu, Zhao, Wei, Han, Yan, and Qi have crossed into Qin territory. Realizing too late the purpose behind Li Mu´s truce with Qin, Zheng quickly gathers his advisors to devise a plan to address the six-state coalition army on their doorstep. For the first time in history, the state of Qin faces complete destruction and must use every resource and strategy at their disposal to prevent themselves from being wiped off the map.',
            'Category': 'Series',
            'genres': ['Action']
            },
            {
			'anime_id': 83,
			'titel': 'Fighting Spirit: New Challenger',
            'releasedate': 'Jan 6 2009',
            'score': 85,
            'summary': 'Ippo Makunouchi continues his boxing career and his goal on knowing the meaning of being strong, and the desire on fighting his idol Ichiro Miyata once again. Along him are pro boxers Takamura, Aoki and Kimura that each one of them aspire to their own dreams.',
            'Category': 'Series',
            'genres': ['Comedy', 'Drama', 'Sports']
            },
            {
			'anime_id': 84,
			'titel': 'HAIKYU‼ TO THE TOP Part 2',
            'releasedate': 'Oct 3 2020',
            'score': 85,
            'summary': 'The second half of Haikyuu!! 4th season kicks-off where the first part ended. Karasuno High won their first match of The Spring Nationals against Tsubakihara Academy. Karasuno High is excited to be back in the Spring Nationals after many years of not making it, so can they handle the pressure of playing against the best teams in Japan? Will they make it to the top?',
            'Category': 'Series',
            'genres': ['Comedy', 'Drama', 'Sports']
            },
            {
			'anime_id': 85,
			'titel': 'JUJUTSU KAISEN',
            'releasedate': 'Oct 3 2020',
            'score': 85,
            'summary': 'A boy fights... for "the right death." Hardship, regret, shame: the negative feelings that humans feel become Curses that lurk in our everyday lives. The Curses run rampant throughout the world, capable of leading people to terrible misfortune and even death. What´s more, the Curses can only be exorcised by another Curse. Itadori Yuji is a boy with tremendous physical strength, though he lives a completely ordinary high school life. One day, to save a friend who has been attacked by Curses, he eats the finger of the Double-Faced Specter, taking the Curse into his own soul. From then on, he shares one body with the Double-Faced Specter. Guided by the most powerful of sorcerers, Gojou Satoru, Itadori is admitted to the Tokyo Metropolitan Technical High School of Sorcery, an organization that fights the Curses... and thus begins the heroic tale of a boy who became a Curse to exorcise a Curse, a life from which he could never turn back.',
            'Category': 'Series',
            'genres': ['Action', 'Drama', 'Supernatural']
            },
            {
			'anime_id': 86,
			'titel': 'Attack on Titan Season 3',
            'releasedate': 'Jul 23 2018',
            'score': 85,
            'summary': 'Eren and his companions in the 104th are assigned to the newly-formed Levi Squad, whose assignment is to keep Eren and Historia safe given Eren´s newly-discovered power and Historia´s knowledge and pedigree. Levi and Erwin have good reason to be concerned, because the priest of the Church that Hanji had hidden away was found tortured to death, making it clear that the Military Police are involved with the cover-up. Things get more harrowing when the MPs make a move on Erwin and the Levi Squad narrowly avoids capture. Eren is also having problems with his Titan transformation, and a deadly killer has been hired to secure Eren and Historia, one Levi knows all too well from his youth.',
            'Category': 'Series',
            'genres': ['Action', 'Drama', 'Fantasy', 'Mystery']
            },
            {
			'anime_id': 87,
			'titel': 'Violet Evergarden',
            'releasedate': 'Jan 11 2018',
            'score': 85,
            'summary': 'A certain point in time, in the continent of Telesis. The great war which divided the continent into North and South has ended after four years, and the people are welcoming a new generation. Violet Evergarden, a young girl formerly known as “the weapon”, has left the battlefield to start a new life at CH Postal Service. There, she is deeply moved by the work of “Auto Memories Dolls”, who carry people´s thoughts and convert them into words. Violet begins her journey as an Auto Memories Doll, and comes face to face with various people´s emotions and differing shapes of love. There are words Violet heard on the battlefield, which she cannot forget. These words were given to her by someone she holds dear, more than anyone else. She does not yet know their meaning but she searches to find it.',
            'Category': 'Series',
            'genres': ['Drama', 'Fantasy', 'Slice of Life']
            },
            {
			'anime_id': 88,
			'titel': 'Neon Genesis Evangelion: The End of Evangelion',
            'releasedate': 'Jul 19 1997',
            'score': 85,
            'summary': 'NERV faces a brutal attack from SEELE, but with Asuka in a coma, and Shinji in a nervous breakdown, things soon turn into the surreal. This movie provides a concurrent ending to the final two episodes of the show Neon Genesis Evangelion.',
            'Category': 'Movie',
            'genres': ['Action', 'Drama', 'Mecha', 'Psychological', 'Sci-Fi']
            },
            {
			'anime_id': 89,
			'titel': 'Kimi ni Todoke: From Me to You Season 3',
            'releasedate': 'Aug 1 2024',
            'score': 85,
            'summary': 'The third season of Kimi ni Todoke. What do you do once you´re a couple? Although she struggles with her blossoming feelings, Sawako comes to terms with herself and tells Kazehaya how she feels about him. Attracted by Sawako´s unnoticed efforts and genuine personality, Kazehaya also candidly makes his feelings known. Thus, their new relationship begins. Their first date, their school life together, joy, embarrassment and new struggles — everything is fresh and new as the couple awkwardly and gradually learns more about one another, all while their friend´ love stories begin to take shape as well. This bittersweet and poignant story of young people, woven from their romantic feelings and dear friendships, begins once more.',
            'Category': 'ONA',
            'genres': ['Comedy', 'Drama', 'Romance', 'Slice of Life']
            },
            {
			'anime_id': 90,
			'titel': 'Cyberpunk: Edgerunners',
            'releasedate': 'Sep 13 2022',
            'score': 85,
            'summary': 'An original anime series set in in the universe of Cyberpunk 2077. Cyberpunk: Edgerunners tells a standalone, 10-episode story about a street kid trying to survive in a technology and body modification-obsessed city of the future. Having everything to lose, he chooses to stay alive by becoming an edgerunner—a mercenary outlaw also known as a cyberpunk.',
            'Category': 'ONA',
            'genres': ['Action', 'Drama', 'Psychological', 'Sci-Fi']
            },
            {
			'anime_id': 91,
			'titel': 'Natsume´s Book of Friends Season 4',
            'releasedate': 'Jan 3 2012',
            'score': 85,
            'summary': 'The fourth season of Natsume Yuujinchou. Still in possession of his grandmother´s Book of Friends, Natsume spends his days returning the names of yokai to their rightful owners. He has been learning how to deal with the yokai and humans that surround his life, but the time has come for him to deal with something even more difficult — his own past, and future.',
            'Category': 'Series',
            'genres': ['Drama', 'Fantasy', 'Slice of Life', 'Supernatural']
            },
            {
			'anime_id': 92,
			'titel': 'Gintama',
            'releasedate': 'Apr 4 2006',
            'score': 85,
            'summary': 'Life isn´t easy in feudal Japan... especially since the aliens landed and conquered everything! Oh sure, the new health care is great, but the public ban on the use of swords has left a lot of defeated samurai with a difficult decision to make concerning their future career paths! This is especially true if, as in the case of Gintoki Sakata, they´re not particularly inclined towards holding a day job, which is why Gintoki´s opted for the freelance route, taking any job that´s offered to him as long as the financial remuneration sounds right. Unfortunately, in a brave new world filled with stray bug-eyed monsters, upwardly mobile Yakuza and overly ambitious E.T. entrepreneurs, those jobs usually don´t pay as well as they should for the pain, suffering and indignities endured!',
            'Category': 'Series',
            'genres': ['Action', 'Comedy', 'Drama', 'Sci-Fi']
            },
            {
			'anime_id': 93,
			'titel': 'Perfect Blue',
            'releasedate': 'Feb 28 1998',
            'score': 85,
            'summary': 'Rising pop star Mima has quit singing to pursue a career as an actress and model, but her fans aren’t ready to see her go... Encouraged by her managers, Mima takes on a recurring role on a popular TV show, when suddenly her handlers and collaborators begin turning up murdered. Harboring feelings of guilt and haunted by visions of her former self, Mima’s reality and fantasy meld into a frenzied paranoia. As her stalker closes in, in person and online, the threat he poses is more real than even Mima knows, in this iconic psychological thriller that has frequently been hailed as one of the most important animated films of all time.',
            'Category': 'Movie',
            'genres': ['Drama', 'Horror', 'Psychological', 'Thriller']
            },
            {
			'anime_id': 94,
			'titel': 'Delicious in Dungeon',
            'releasedate': 'Jan 4 2024',
            'score': 85,
            'summary': 'When young adventurer Laios and his company are attacked and soundly thrashed by a dragon deep in a dungeon, the party loses all its money and provisions...and a member! They´re eager to go back and save her, but there is just one problem: If they set out with no food or coin to speak of, they´re sure to starve on the way! But Laios comes up with a brilliant idea: "Let´s eat the monsters!" Slimes, basilisks, and even dragons...none are safe from the appetites of these dungeon-crawling gourmands!',
            'Category': 'Series',
            'genres': ['Adventure', 'Comedy', 'Fantasy']
            },
            {
			'anime_id': 95,
			'titel': 'Oshi No Ko',
            'releasedate': 'Apr 12 2023',
            'score': 85,
            'summary': 'When a pregnant young starlet appears in Gorou Amemiya’s countryside medical clinic, the doctor takes it upon himself to safely (and secretly) deliver Ai Hoshino’s child so she can make a scandal-free return to the stage. But no good deed goes unpunished, and on the eve of her delivery, he finds himself slain at the hands of Ai’s deluded stalker — and subsequently reborn as Ai’s child, Aquamarine Hoshino! The glitz and glamor of showbiz hide the dark underbelly of the entertainment industry, threatening to dull the shine of his favorite star. Can he help his new mother rise to the top of the charts? And what will he do when unthinkable disaster strikes?',
            'Category': 'Series',
            'genres': ['Drama', 'Mystery', 'Psychological', 'Supernatural']
            },
            {
			'anime_id': 96,
			'titel': 'Natsume´s Book of Friends Season 6',
            'releasedate': 'Apr 12 2017',
            'score': 85,
            'summary': 'The sixth season of Natsume Yuujinchou.',
            'Category': 'Series',
            'genres': ['Drama', 'Fantasy', 'Slice of Life', 'Supernatural']
            },
            {
			'anime_id': 97,
			'titel': 'Made in Abyss',
            'releasedate': 'Jul 7 2017',
            'score': 85,
            'summary': 'The "Abyss" is the last unexplored place in the world. Strange and wonderful creatures roam within, and it is full of precious relics that present humans can´t recreate. Those that dare to explore the depths are known as "Cave Raiders." An orphan girl named Riko lives on the rim. Her dream is to become a Cave Raider like her mother and solve the mysteries of the cave system. One day, Riko starts exploring the caves and discovers a robot who resembles a human boy.',
            'Category': 'Series',
            'genres': ['Adventure', 'Drama', 'Fantasy', 'Horror', 'Mystery', 'Sci-Fi']
            },
            {
			'anime_id': 98,
			'titel': 'Kizumonogatari Part 2: Nekketsu',
            'releasedate': 'Aug 19 2016',
            'score': 85,
            'summary': 'First season of the Monogatari Series, part 3/6. Contains the arc Koyomi Vamp from the Kizumonogatari light novel. In the spring of his second year of high school, Koyomi Araragi met the beautiful vampire Kiss-Shot Acerola-Orion Heart-Under-Blade. Koyomi saved Kiss-shot, who was on the verge of death with all four of her limbs cut off, but only at the expense of becoming her minion and a vampire. “In order to go back to being a human again, you must take back all of Kiss-shot’s limbs.” After receiving advice from Meme Oshino, an expert in the supernatural, Koyomi prepares to go into battle. Awaiting him are three powerful vampire hunters—Dramaturgy, a giant vampire hunter who is a vampire himself. Episode, a half-vampire who wields an enormous cross, and Guillotinecutter, a quiet man who specializes in killing vampires. Will Koyomi be able to take back Kiss-Shot’s limbs from the vampire hunters? Amidst the soft spring rain, the curtain rises on this fateful blood bath…',
            'Category': 'Movie',
            'genres': ['Action', 'Drama', 'Ecchi', 'Mystery', 'Psychological', 'Supernatural']
            },
            {
			'anime_id': 99,
			'titel': 'Gurren Lagann',
            'releasedate': 'Apr 1 2007',
            'score': 85,
            'summary': 'In a far away future, mankind lives underground in huge caves, unknowing of a world above with a sky and stars. In the small village of Jiha, Simon, a shy boy who works as a digger discovers a strange glowing object during excavation. The enterprising Kamina, a young man with a pair of rakish sunglasses and the passion of a firey sun, befriends Simon and forms a small band of brothers, the Gurren Brigade, to escape the village and break through the ceiling of the cave to reach the surface, which few believe exist. The village elder won´t hear of such foolishness and punishes the Brigade. However, when disaster strikes from the world above and the entire village is in jeopardy, it´s up to Simon, Kamina, a girl with a big gun named Yoko, and the small yet sturdy robot, Lagann, to save the day. The new friends journey to the world above and find that the surface is a harsh battlefield, and it´s up to them to fight back against the rampaging Beastmen to turn the tide in the humans´favor! Pierce the heavens, Gurren Lagann!',
            'Category': 'Series',
            'genres': ['Action', 'Comedy', 'Drama', 'Mecha', 'Romance', 'Sci-Fi']
            },
            {
			'anime_id': 100,
			'titel': 'MUSHI-SHI',
            'releasedate': 'Oct 23 2005',
            'score': 85,
            'summary': 'Neither good nor evil, they are life in its purest form. Vulgar and strange, they have inspired fear in humans since the dawn of time and have, over the ages, come to be known as "mushi." The stories of the Mushi and the people they affect are all linked together by a traveling Mushi-shi, or "Mushi Master," who seeks rare Mushi sightings and uses his shaman-like knowledge of Mushi to help the affected people. What are the Mushi and what do they want',
            'Category': 'Series',
            'genres': ['Adventure', 'Fantasy', 'Mystery', 'Psychological', 'Slice of Life', 'Supernatural']
            },

    ]

    with app.app_context():
        for anime_data in initial_anime:
            try:
                # Genres erstellen/finden
                genre_objs = []
                for genre_name in anime_data['genres']:
                    genre = Genre.query.filter_by(name=genre_name).first()
                    if not genre:
                        genre = Genre(name=genre_name)
                        db.session.add(genre)
                    genre_objs.append(genre)

                # Neuen Anime erstellen
                new_anime = AnimeList(
                    titel=anime_data['titel'],
                    releasedate=anime_data['releasedate'],
                    score=anime_data['score'],
                    summary=anime_data['summary'],
                    Category=anime_data['Category']
                )
                new_anime.genres = genre_objs
                
                db.session.add(new_anime)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(f"Fehler beim Hinzufügen von Anime: {e}")

def add_images_to_anime(app, api_key):
    """
    Fügt den Anime-Einträgen Bild-URLs aus der TMDB API hinzu.
    Ruft diese Funktion NUR EINMALIG auf, z. B. per CLI-Kommando.
    """
    base_tv_url = "https://api.themoviedb.org/3/search/tv"
    base_movie_url = "https://api.themoviedb.org/3/search/movie"
    image_base_url = "https://image.tmdb.org/t/p/w500"  # Basis-URL für Bilder

    with app.app_context():
        animes = AnimeList.query.all()  # Alle Anime aus der DB holen

        for anime in animes:
            try:
                # Nur aktualisieren, wenn KEINE image_url vorhanden ist
                if anime.image_url:
                    continue

                if anime.Category == "Series":
                    base_url = base_tv_url
                elif anime.Category == "Movie":
                    base_url = base_movie_url
                else:
                    # Sonst 'Special', 'OVA', etc. – kann man ggf. handle(n)
                    print(f"Unbekannte Kategorie für '{anime.titel}': {anime.Category}")
                    continue

                response = requests.get(base_url, params={
                    'api_key': api_key,
                    'query': anime.titel
                })
                data = response.json()

                if data.get('results'):
                    first_result = data['results'][0]
                    poster_path = first_result.get('poster_path')
                    if poster_path:
                        anime.image_url = f"{image_base_url}{poster_path}"
                        db.session.commit()
                        print(f"Bild für '{anime.titel}' hinzugefügt.")
                    else:
                        print(f"Kein poster_path für '{anime.titel}' gefunden.")
                else:
                    print(f"Kein Treffer für '{anime.titel}' gefunden.")

            except Exception as e:
                print(f"Fehler bei '{anime.titel}': {e}")
                db.session.rollback()