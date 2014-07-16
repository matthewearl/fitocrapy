import abc
import getpass
import http.client
import http.cookiejar
import re
import urllib.parse
import urllib.request

#http.client.HTTPConnection.debuglevel = 1 

class Fitocracy(metaclass=abc.ABCMeta):
    BASE_URL = "https://www.fitocracy.com"
    HOME_URL = BASE_URL + "/"
    LOGIN_URL = BASE_URL + "/accounts/login/"
    USER_AGENT = ("Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) "
                    "Gecko/20100101 Firefox/30.0")


    @abc.abstractmethod
    def _get_credentials(self):
        raise NotImplementedError


    def _open(self, url, data=None, headers=None):
        assert self._opener is not None
        
        if headers is None:
            headers = {}

        req = urllib.request.Request(url, data)
        req.add_header("User-Agent", self.USER_AGENT)
        for key, val in headers.items():
            req.add_header(key, val)
        return self._opener.open(req, data=data)


    def login(self):
        # Build an opener which will maintain a set of cookies for this
        # session.
        self._cj = http.cookiejar.CookieJar()
        self._opener = urllib.request.build_opener(
                        urllib.request.HTTPCookieProcessor(self._cj))

        # Pull the homepage, and grab the anti-XSS hidden form element. This is 
        # used by the server to associate a given log in attempt with a
        # particular instance of the login form.
        f = self._open(self.HOME_URL)
        homepage = f.read().decode('utf-8')
        m = re.match(
            r".*'csrfmiddlewaretoken' value='([a-f0-9]*)'.*",
            homepage, re.S)
        if m is None:
            raise Exception("No csrfmiddlewaretoken on home page")
        csrfmiddlewaretoken = m.group(1)

        # Obtain the username and password.
        uname, pword = self._get_credentials()

        # Actually log in.
        data = urllib.parse.urlencode({
                                    'csrfmiddlewaretoken': csrfmiddlewaretoken,
                                    'is_username': 1,
                                    'json': 1,
                                    'next': '/home/',
                                    'username': uname,
                                    'password': pword,
                                  }).encode('utf-8')
        f = self._open(self.LOGIN_URL, data,
                       headers={
                        'Content-Type':
                            'application/x-www-form-urlencoded;charset=utf-8',
                        'Referer':
                            self.HOME_URL,
                       })
        print(f.read())


    def get_group_members(self, group_id):
        raise NotImplementedError


class FitocracyPromptLogin(Fitocracy):
    def _get_credentials(self):
        uname = input("Username: ")
        pword = getpass.getpass()

        return uname, pword


if __name__ == "__main__":
    f = FitocracyPromptLogin()
    f.login()


