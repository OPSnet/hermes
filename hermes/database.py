"""
Utility module that maps the various gazelle tables to SQLAlchemy classes so
that we can use them nicely within hermes and not have to do something dumb
like escaping our inputs for use within DB queries (like zookeeper).
"""

from sqlalchemy import create_engine, ForeignKey, Column
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy.dialects.mysql as mysql
from sqlalchemy.orm import sessionmaker, relationship
from phpserialize import unserialize

from hermes.utils import dict_to_list

BASE = declarative_base()


class GazelleDB(object):
    """
    Primary class that is used by hermes to load the DB, and manage it's connection. We then
    define functions for the interactions that we expect to have with the DB as well such that
    we are not directly exposing the interface to the end-user so that we're not allowing
    any arbitrary statement in any of the arbitrary modules.
    """
    def __init__(self, host, db_name, username, password):
        self._engine = create_engine("mysql+pymysql://{}:{}@{}:33060/{}"
                                     .format(username, password, host, db_name), pool_recycle=3600)
        self._session_maker = sessionmaker(bind=self._engine, autocommit=True)
        self._session = self._session_maker()

    def get_user(self, username):
        """
        Given a username, get the User that it matches, else return None

        :param username:
        :return: User that the username belongs to if one exists
        :rtype: User
        """
        return self._session.query(User).filter_by(username=username).first()

    def get_topic(self, topic_id):
        """
        Given a topic id, get the Topic that it matches, else return None

        :param topic_id:
        :return: ForumTopics that topic_id belongs to if one exists
        :rtype: ForumTopics
        """
        return self._session.query(ForumTopics).filter_by(id=int(topic_id)).first()

    def disconnect(self):
        self._session.close()
        self._engine.dispose()


class ForumTopics(BASE):
    __tablename__ = "forums_topics"
    id = Column('ID', mysql.INTEGER(10, unsigned=True), primary_key=True, autoincrement=True)
    title = Column('Title', mysql.VARCHAR(150))
    author_id = Column('AuthorID', mysql.INTEGER(10))
    is_locked = Column('IsLocked', mysql.ENUM('0', '1'), default='0')
    is_sticky = Column('IsSticky', mysql.ENUM('0', '1'), default='1')
    forum_id = Column('ForumID', mysql.INTEGER(3))
    num_posts = Column('NumPosts', mysql.INTEGER(10))
    last_post_id = Column('LastPostID', mysql.INTEGER(10))
    last_post_time = Column('LastPostTime', mysql.DATETIME())
    last_post_author_id = Column('LastPostAuthorID', mysql.INTEGER(10))
    sticky_post_id = Column('StickyPostID', mysql.INTEGER(10))
    ranking = Column('Ranking', mysql.TINYINT(2))
    created_time = Column('CreatedTime', mysql.DATETIME())


class Permissions(BASE):
    __tablename__ = "permissions"
    id = Column('ID', mysql.INTEGER(10, unsigned=True), primary_key=True, autoincrement=True)
    level = Column('Level', mysql.INTEGER(10, unsigned=True), unique=True)
    name = Column('Name', mysql.VARCHAR(25))
    values = Column('Values', mysql.TEXT)
    display_staff = Column('DisplayStaff', mysql.ENUM('0', '1'), default='0')
    permitted_forums = Column('PermittedForums', mysql.VARCHAR(150))
    secondary = Column('Secondary', mysql.TINYINT(4))


class UserInfo(BASE):
    __tablename__ = "users_info"
    user_id = Column("UserID", mysql.INTEGER(10, unsigned=True), ForeignKey('users_main.ID'),
                     primary_key=True)
    style_id = Column("StyleID", mysql.INTEGER(10, unsigned=True))
    style_url = Column("StyleURL", mysql.VARCHAR(255))
    info = Column("Info", mysql.TEXT)
    avatar = Column("Avatar", mysql.VARCHAR(255))
    admin_comments = Column("AdminComment", mysql.TEXT)
    site_options = Column("SiteOptions", mysql.TEXT)
    view_avatars = Column("ViewAvatars", mysql.ENUM('0', '1'))
    donor = Column('Donor', mysql.ENUM('0', '1'))
    artist = Column('Artist', mysql.ENUM('0', '1'))
    download_alt = Column('DownloadAlt', mysql.ENUM('0', '1'))
    warned = Column('Warned', mysql.DATETIME)
    support_for = Column('SupportFor', mysql.VARCHAR(255))
    torrent_grouping = Column('TorrentGrouping', mysql.ENUM('0', '1', '2'))
    show_tags = Column('ShowTags', mysql.ENUM('0', '1'))
    notify_on_quote = Column('NotifyOnQuote', mysql.ENUM('0', '1', '2'))
    auth_key = Column('AuthKey', mysql.VARCHAR(32))
    reset_key = Column('ResetKey', mysql.VARCHAR(32))
    reset_expires = Column('ResetExpires', mysql.DATETIME)
    join_date = Column('JoinDate', mysql.DATETIME)
    inviter = Column('Inviter', mysql.INTEGER(10))
    bitcoin_address = Column('BitcoinAddress', mysql.VARCHAR(34))
    warned_times = Column('WarnedTimes', mysql.INTEGER(2))
    disable_avatar = Column('DisableAvatar', mysql.ENUM('0', '1'))
    disable_posting = Column('DisableInvites', mysql.ENUM('0', '1'))
    disable_forums = Column('DisableForums', mysql.ENUM('0', '1'))
    disable_irc = Column('DisableIRC', mysql.ENUM('0', '1'))
    disable_tagging = Column('DisableTagging', mysql.ENUM('0', '1'))
    disable_upload = Column('DisableUpload', mysql.ENUM('0', '1'))
    disable_wiki = Column('DisableWiki', mysql.ENUM('0', '1'))
    disable_pm = Column('DisablePM', mysql.ENUM('0', '1'))
    ratio_watch_ends = Column('RatioWatchEnds', mysql.DATETIME)
    ratio_watch_download = Column('RatioWatchDownload', mysql.BIGINT(20, unsigned=True))
    ratio_watch_times = Column('RatioWatchTimes', mysql.TINYINT(1, unsigned=True))
    ban_date = Column('BanDate', mysql.DATETIME)
    ban_reason = Column('BanReason', mysql.ENUM('0', '1', '2', '3', '4'))
    catchup_time = Column('CatchupTime', mysql.DATETIME)
    last_read_news = Column('LastReadNews', mysql.INTEGER(10))
    hide_country_changes = Column('HideCountryChanges', mysql.ENUM('0', '1'))
    restricted_forums = Column('RestrictedForums', mysql.VARCHAR(150))
    disable_requests = Column('DisableRequests', mysql.ENUM('0', '1'))
    permitted_forums = Column('PermittedForums', mysql.VARCHAR(150))
    unseeded_alerts = Column('UnseededAlerts', mysql.ENUM('0', '1'))
    last_read_blog = Column('LastReadBlog', mysql.ENUM('0', '1'))
    info_title = Column('InfoTitle', mysql.VARCHAR(255))


class User(BASE):
    __tablename__ = "users_main"
    id = Column("ID", mysql.INTEGER(10, unsigned=True), primary_key=True)
    username = Column('Username', mysql.VARCHAR(20))
    email = Column('Email', mysql.VARCHAR(255))
    pass_hash = Column('PassHash', mysql.VARCHAR(60))
    secret = Column('Secret', mysql.VARCHAR(32))
    irc_key = Column('IRCKey', mysql.CHAR(32))
    last_login = Column('LastLogin', mysql.DATETIME)
    last_access = Column('LastAccess', mysql.DATETIME)
    ip = Column('IP', mysql.VARCHAR(15))
    class_id = Column('Class', mysql.TINYINT(2))
    uploaded = Column('Uploaded', mysql.BIGINT(20, unsigned=True))
    downloaded = Column('Downloaded', mysql.BIGINT(20, unsigned=True))
    title = Column('Title', mysql.TEXT)
    enabled = Column('Enabled', mysql.ENUM('0', '1', '2'))
    paranoia = Column('Paranoia', mysql.TEXT)
    visible = Column('Visible', mysql.ENUM('1', '0'))
    invites = Column('Invites', mysql.INTEGER(10, unsigned=True))
    permission_id = Column('PermissionID', mysql.INTEGER(10, unsigned=True),
                           ForeignKey('permissions.ID'))
    custom_permissions = Column('CustomPermissions', mysql.TEXT)
    can_leech = Column('can_leech', mysql.TINYINT(4))
    torrent_pass = Column('torrent_pass', mysql.CHAR(32))
    required_ratio = Column('RequiredRatio', mysql.DOUBLE(10, 8))
    required_ratio_work = Column('RequiredRatioWork', mysql.DOUBLE(10, 8))
    ipcc = Column('ipcc', mysql.VARCHAR(2))
    fl_tokens = Column('FLTokens', mysql.INTEGER(10))

    permission_class = relationship("Permissions")

    info = relationship("UsersInfo")

    def get_paranoia(self):
        return dict_to_list(unserialize(bytes(str(self.paranoia), 'utf-8')))
