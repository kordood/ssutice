from time import sleep
import threading

from misc.pickle_io import load_pickle, save_pickle
from crawler.utils import merge_to_anchor, find_new_notice
from .post import post_to_slack


class NoticeBot(threading.Thread):

    def __init__(self, crawl_func, webhook_url, info_path, seek_time=43200):
        threading.Thread.__init__(self)
        self.get_notice_list = crawl_func
        self.webhook_url = webhook_url
        self.info_path = info_path
        self.seek_time = seek_time

    @staticmethod
    def announce_notices_to_slack(notices, webhook_url):
        for notice in notices:
            post_to_slack(
                merge_to_anchor(notice[0], notice[1]),
                webhook_url
            )

    def run(self):
        while True:
            past_notice = load_pickle(self.info_path)
            current_notice = self.get_notice_list()

            if past_notice is None:
                past_notice = current_notice
                self.announce_notices_to_slack(current_notice, self.webhook_url)
                save_pickle(current_notice, self.info_path)

            else:
                new_notices = find_new_notice(past_notice, current_notice)

                if new_notices is not []:
                    self.announce_notices_to_slack(new_notices, self.webhook_url)
                    save_pickle(current_notice, self.info_path)

            sleep(self.seek_time)
