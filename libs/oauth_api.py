# -*- coding: utf-8 -*-
"""
Propose: 
Author: 'yac'
Date: 
"""

import tornado
from tornado import web, auth, gen, escape

from user.social_user_api import SocialUser
from user.user_api import User
from libs.conf import TW_KEY, TW_SECRET, FB_KEY, FB_SECRET
from user.app_user import BaseHandler

from logger import ac as log

class FacebookGraphLoginHandler(BaseHandler, auth.FacebookGraphMixin):

    @tornado.web.asynchronous
    def get(self):
        my_url = (self.request.protocol + '://' + self.request.host + '/oauth/fb')

        if self.get_argument('code', False):
            self.get_authenticated_user(
                redirect_uri=my_url,
                client_id=FB_KEY,
                client_secret=FB_SECRET,
                code=self.get_argument('code'),
                callback=self._on_auth)
            return

        self.authorize_redirect(redirect_uri=my_url,
                                client_id=FB_KEY,
                                extra_params={'scope': 'email, user_events'})

    def _on_auth(self, fb_user):
        if not fb_user:
            raise tornado.web.HTTPError(500, "Facebook auth failed")

        social_user = SocialUser(User(login=fb_user['id']))

        social_user.params = {'login': fb_user['id'],
                              'access_token': fb_user['access_token'],
                              'social_net': 'fb',
                              'email': fb_user.get('email'),
                              'name': fb_user['name'].encode('utf-8'),
                              'profile_url': fb_user['link']}

        social_user.save_to_db()

        self.set_secure_cookie("login", str(fb_user['id']))
        self.set_secure_cookie("user_id", str(social_user.user_db.id))
        # self.redirect('/user/%s' % social_user.user_db.id)
        self.redirect('/home')

oauth_handlers = [(r"/oauth/fb", FacebookGraphLoginHandler)]


#oauth = OAuth()
#twitter = oauth.remote_app('twitter',
#                           base_url='https://api.twitter.com/1.1/',
#                           request_token_url='https://api.twitter.com/oauth/request_token',
#                           access_token_url='https://api.twitter.com/oauth/access_token',
#                           authorize_url='https://api.twitter.com/oauth/authorize',
#                           consumer_key=app.config['TW_KEY'],
#                           consumer_secret=app.config['TW_SECRET']
#)
#
#facebook = oauth.remote_app('facebook',
#                            base_url='https://graph.facebook.com/',
#                            request_token_url=None,
#                            access_token_url='/oauth/access_token',
#                            authorize_url='https://www.facebook.com/dialog/oauth',
#                            consumer_key=app.config['FB_KEY'],
#                            consumer_secret=app.config['FB_SECRET'],
#                            request_token_params={'scope': 'email, user_events'}
#)
#
#
#@app.route('/oauth/<social>')
#def soc_login(social):
#    if social == 'twitter':
#        return twitter.authorize()
#    elif social == 'fb':
#        return facebook.authorize(callback=app.config['APP_URL'] + '/fb-authorized')
#
#
#################### TWITTER ########################
#@twitter.tokengetter
#def get_twitter_token(token=None):
#    return session.get('oauth_token')
#@app.route('/twitter-authorized')
#@twitter.authorized_handler
#def twitter_authorized(resp):
#    if resp is None:
#        return render_template('index.html', error=u'You denied the request to sign in.')
#
#    social_user = SocialUser(User(login=resp['screen_name']))
#    social_user.params = {'login': resp['screen_name'],
#                          'access_token': resp['oauth_token_secret'],
#                          'social_net': 'twitter'}
#    social_user.env = request.__dict__['environ']
#    social_user.save_to_db()
#
#    login_user(social_user.user_db)
#
#    session['user_id'] = social_user.user.id
#    session['user_login'] = resp['screen_name']
#    session['oauth_token'] = (resp['oauth_token'], resp['oauth_token_secret'])
#
#    return redirect('/user/%s' % social_user.user.id)
#
##################### FACEBOOK #######################
#@facebook.tokengetter
#def get_fb_token(token=None):
#    return session.get('oauth_token')
#@app.route('/fb-authorized')
#@facebook.authorized_handler
#def fb_authorized(resp):
#    if resp is None:
#        return render_template('index.html', error=u'You denied the request to sign in.')
#
#    profile = json.load(urllib.urlopen(
#        "https://graph.facebook.com/me?" +
#        urllib.urlencode(dict(access_token=resp['access_token'])))
#    )
#
#    social_user = SocialUser()
#    social_user.params = {'login': profile['id'],
#                          'access_token': resp['access_token'],
#                          'social_net': 'fb',
#                          'email': profile['email'],
#                          'name': profile['name'],
#                          'profile_url': profile['link'],
#                          }
#    social_user.env = request.__dict__['environ']
#    social_user.save_to_db()
#
#    login_user(social_user.user)
#
#    session['user_id'] = social_user.user.id
#    session['user_login'] = profile['name']
#    session['oauth_token'] = resp['access_token']
#
#    return redirect('/user/%s' % social_user.user.id)

