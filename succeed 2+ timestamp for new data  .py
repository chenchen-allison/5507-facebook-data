import re
import json
import time

import requests
import datetime
import pandas as pd
from retrying import retry # 用于自动重试失败的操作
import warnings # 用于管理警告
from datetime import datetime, timedelta
warnings.filterwarnings("ignore") # 忽略运行中的警告信息
import os

# 初始化参数
class FaceBookKeyWord:
    def __init__(self,cookie_str):
        self.headers = {
            "authority": "www.facebook.com",
            "accept": "*/*",
            "accept-language": "zh-CN,zh;q=0.9",
            "cache-control": "no-cache",
            "content-type": "application/x-www-form-urlencoded",
            "dpr": "0.9",
            "origin": "https://www.facebook.com",
            "pragma": "no-cache",
            "referer": "https://www.facebook.com/search/top?q=web3.0",
            "sec-ch-prefers-color-scheme": "light",
            "sec-ch-ua": "\"Chromium\";v=\"116\", \"Not)A;Brand\";v=\"24\", \"Google Chrome\";v=\"116\"",
            "sec-ch-ua-full-version-list": "\"Chromium\";v=\"116.0.5845.188\", \"Not)A;Brand\";v=\"24.0.0.0\", \"Google Chrome\";v=\"116.0.5845.188\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-model": "\"\"",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-ch-ua-platform-version": "\"8.0.0\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
            "viewport-width": "1066",
            "x-asbd-id": "129477",
            "x-fb-friendly-name": "SearchCometResultsInitialResultsQuery",
            "x-fb-lsd": "Z1-AP4fRU0omV4HbmQqgB2"
        }
        # 转换 cookie 字符串为字典格式
        self.cookies = self.cookie_str_to_dict(cookie_str)
        # 初始化类的其他属性
        self.start_day = None
        self.end_day = None
        self.url = "https://www.facebook.com/api/graphql/"# Facebook 的 API 请求 URL
        self.fb_dtsg = None # 用于身份验证的 token
        self.token = None # 用于身份验证的 token
        self.data_count = 0 # 记录已处理的数据数量

    #将 Cookie 字符串转为字典
    def cookie_str_to_dict(self,cookie_str: str) -> dict:
        cookie_dict = {}
        cookies = cookie_str.split('; ')
        for cookie in cookies:#加入错误处理，忽略无效的 Cookie 键值对
            try:
                key, value = cookie.split('=', 1)
                cookie_dict[key] = value
            except ValueError:
                print(f"无效的 Cookie 项：{cookie}")
        return cookie_dict
 
    def check_cookies_validity(self):
        test_url = "https://www.facebook.com/"
        response = requests.get(test_url, headers=self.headers, cookies=self.cookies)
        if response.status_code == 200 and "登录" not in response.text:
            print("Cookies 有效")
        else:
            print("Cookies 无效，请更新")

    #时间戳转换函数
    def transfromTime(self,ts):# 将时间戳（整数）转为标准时间格式 "YYYY-MM-DD HH:MM:SS"
        date=datetime.fromtimestamp(ts)  # 返回 datetime 对象
        # gmt_offset = datetime.timedelta(hours=8)
        # return (date + gmt_offset).strftime("%Y-%m-%d %H:%M:%S")
        return date.strftime("%Y-%m-%d %H:%M:%S")# 转换为字符串

    @retry(stop_max_attempt_number=5)# 重试装饰器，最多重试 5 次
    def get_init_params(self):# 获取初始请求所需的 token 和参数
        headers_ = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
            "cache-control": "no-cache",
            "dpr": "0.9",
            "pragma": "no-cache",
            "priority": "u=0, i",
            "sec-ch-prefers-color-scheme": "light",
            "sec-ch-ua": "\"Google Chrome\";v=\"129\", \"Not=A?Brand\";v=\"8\", \"Chromium\";v=\"129\"",
            "sec-ch-ua-full-version-list": "\"Google Chrome\";v=\"129.0.6668.101\", \"Not=A?Brand\";v=\"8.0.0.0\", \"Chromium\";v=\"129.0.6668.101\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-model": "\"\"",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-ch-ua-platform-version": "\"8.0.0\"",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": self.headers["user-agent"],
            "viewport-width": "647"
        }
        url = "https://www.facebook.com/"
        response = requests.get(url, headers=headers_, cookies=self.cookies, timeout=(10, 20))
        response.encoding = 'utf-8'
        status = response.status_code# 获取响应状态码
        print("get_init_params请求状态码->", status)
        html = response.text# 获取 HTML 响应
        # 使用正则表达式提取 fb_dtsg 和 token
        #在正则匹配前打印 HTML 内容，确保结构未发生变化
        try:
            self.fb_dtsg = re.findall(r'"DTSGInitialData",\[\],\{"token":"(.*?)"\},', html)[0]
            self.token = re.findall(r'"LSD",\[\],\{"token":"(.*?)"', html)[0]
            print("返回的HTML内容：")
            # print(html)
        except IndexError:
            print("未能匹配到所需的token，请检查正则表达式或HTML结构")
            return
        #保存到文件中
        with open('初始化参数.txt', 'w', encoding="utf-8") as f:
            f.write(f"{self.fb_dtsg}------{self.token}")

    #获取数据
    def get_data(self,keyword,cursor=None):
        # 根据关键词获取数据，cursor 用于分页
        start_year = self.start_day.split("-")[0]# 提取开始年份
        end_year = self.end_day.split("-")[0]
        start_month = "-".join(self.start_day.split("-",)[:-1])# 提取开始月份
        end_month = "-".join(self.end_day.split("-",)[:-1])
        # 构造过滤器参数
        args = {"start_year":start_year,"start_month":start_month,"end_year":end_year,"end_month":end_month,"start_day":self.start_day,"end_day":self.end_day}
        create_time = {"name":"creation_time","args":json.dumps(args,separators=(",",":"))}
        filters = json.dumps([json.dumps(create_time,separators=(",",":"))],separators=(",",":"))
        # 如果是第一页数据
        if not cursor:
            preData = "{\"RELAY_INCREMENTAL_DELIVERY\":true,\"connectionClass\":\"GOOD\",\"feedbackSource\":1,\"feedInitialFetchSize\":2,\"feedLocation\":\"NEWSFEED\",\"feedStyle\":\"DEFAULT\",\"orderby\":[\"TOP_STORIES\"],\"privacySelectorRenderLocation\":\"COMET_STREAM\",\"recentVPVs\":[],\"refreshMode\":\"AUTO\",\"renderLocation\":\"homepage_stream\",\"scale\":2,\"shouldChangeBRSLabelFieldName\":false,\"shouldObfuscateCategoryField\":false,\"useDefaultActor\":false,\"__relay_internal__pv__GHLShouldChangeSponsoredAuctionDistanceFieldNamerelayprovider\":false,\"__relay_internal__pv__GHLShouldChangeSponsoredDataFieldNamerelayprovider\":false,\"__relay_internal__pv__GHLShouldChangeAdIdFieldNamerelayprovider\":false,\"__relay_internal__pv__IsWorkUserrelayprovider\":false,\"__relay_internal__pv__CometFeedStoryDynamicResolutionPhotoAttachmentRenderer_experimentWidthrelayprovider\":500,\"__relay_internal__pv__CometImmersivePhotoCanUserDisable3DMotionrelayprovider\":false,\"__relay_internal__pv__IsMergQAPollsrelayprovider\":false,\"__relay_internal__pv__FBReelsMediaFooter_comet_enable_reels_ads_gkrelayprovider\":false,\"__relay_internal__pv__CometUFIReactionsEnableShortNamerelayprovider\":false,\"__relay_internal__pv__CometUFIShareActionMigrationrelayprovider\":true,\"__relay_internal__pv__StoriesArmadilloReplyEnabledrelayprovider\":false,\"__relay_internal__pv__EventCometCardImage_prefetchEventImagerelayprovider\":false}\""%(filters,keyword)
        else:
            # 如果不是第一页数据，传入分页 cursor
            preData = "{\"allow_streaming\":false,\"args\":{\"callsite\":\"COMET_GLOBAL_SEARCH\",\"config\":{\"exact_match\":false,\"high_confidence_config\":null,\"intercept_config\":null,\"sts_disambiguation\":null,\"watch_config\":null},\"context\":{\"bsid\":\"2e9faf29-5317-4395-99d4-b94c9aafc69b\",\"tsid\":\"0.4195531988320449\"},\"experience\":{\"encoded_server_defined_params\":null,\"fbid\":null,\"type\":\"POSTS_TAB\"},\"filters\":%s,\"text\":\"%s\"},\"count\":5,\"cursor\":\"%s\",\"feedLocation\":\"SEARCH\",\"feedbackSource\":23,\"fetch_filters\":true,\"focusCommentID\":null,\"locale\":null,\"privacySelectorRenderLocation\":\"COMET_STREAM\",\"renderLocation\":\"search_results_page\",\"scale\":1,\"stream_initial_count\":0,\"useDefaultActor\":false,\"__relay_internal__pv__IsWorkUserrelayprovider\":false,\"__relay_internal__pv__IsMergQAPollsrelayprovider\":false,\"__relay_internal__pv__CometUFIReactionsEnableShortNamerelayprovider\":false,\"__relay_internal__pv__StoriesArmadilloReplyEnabledrelayprovider\":false,\"__relay_internal__pv__StoriesRingrelayprovider\":false}"%(filters,keyword,cursor)
        # 请求的数据 payload
        self.data = {
            "av": self.cookies['c_user'],
            "__aaid": "0",
            "__user": self.cookies['c_user'],
            "__a": "1",
            "__req": "22",
            "__hs": "20045.HYP:comet_pkg.2.1..2.1",
            "dpr": "1",
            "__ccg": "EXCELLENT",
            "__rev": "1018274683",
            "__s": "fh64kx:tga794:fsitcn",
            "__hsi": "7438464302859897339",
            "__dyn": "7AzHK4HwkEng5K8G6EjBAg5S3G2O5U4e2C17xt3odE98K360CEboG0x8bo6u3y4o2Gwn82nwb-q7oc81EEc87m221Fwgo9oO0-E4a3a4oaEnxO0Bo7O2l2Utwqo31wiE567Udo5qfK0zEkxe2GewGwkUe9obrwh8lwUwgojUlDw-wSU8o4Wm7-2K1yw9q2-VEbUGdG0HE88cA0z8c84q58jyUaUcojxK2B08-269wkopg6C13whEeE-3WVU-4EdrxG1fBG2-2K2G0JU",
            "__csr": "gbk7Yj2AYegPis9FjPRtbTsgD9d7qiHkLfAuKyZd_8BbPnnrbGgG-hegLejFEN27G9ltdbF4ihyqHXChrGHyurBBGjKUjHGjGuFmaCFfy4KUgx1Bz8Ci8BBG8ixunzUy6FoSqujKi9DGfCxqi8K79Uqxq9gggaoC4HxiEvxCt1DwBxO2m4oDwJy85G9x248beUhwgUSfw960BEc8qyEgxO0m-1ywyw8m1kw47w5mwbe2i0pW0te0b5a0RE9Fo3dw3XE06oq02bm00PkA1ryU094U2Gwroqw2Rof8rwmo2mw3Po8UdV2o0Ta02VS7o",
            "__comet_req": "15",
            "fb_dtsg": self.fb_dtsg,
            "jazoest": "25676",
            "lsd": self.token,
            "__spin_r": "1018274683",
            "__spin_b": "trunk",
            "__spin_t": str(int(time.time())),
            "fb_api_caller_class": "RelayModern",
            "fb_api_req_friendly_name": "SearchCometResultsPaginatedResultsQuery",
            "variables": preData,
            "server_timestamps": "true",
            "doc_id": "8633218593432726"
        }

    #发送请求
    def get(self):
        # 向 Facebook API 发送 POST 请求并返回响应
        # time.sleep(random.random() * 2)
        while True:
            try:
                response = requests.post(self.url,
                                         headers=self.headers,
                                         cookies=self.cookies,
                                         data=self.data,
                                         verify=False,
                                         timeout=(3,10))
                status = response.status_code# 获取响应状态码
                if status == 200:
                    text = response.content.decode()# 返回解码后的响应内容
                    return text
            except Exception as e:
                print("请求发生错误：", e)

    #数据解析
    def parse_data(self, keyword, edges):# 解析返回的 JSON 数据
        resultList = []
        for edge in edges:
            try:
                # 解析帖子相关信息，例如内容、用户、时间等
                s = edge["relay_rendering_strategy"]["view_model"]["click_model"]["story"]
                post_id = s.get("post_id")# 帖子 ID
                comment_id = s.get('feedback', {}).get("id")
                story = s["comet_sections"]["content"]["story"]
                message = story.get("message")
                if message:
                    content = message.get("text")
                else:
                    content = None
                if not content:
                    try:
                        content = story["attachments"][0]["styles"]["attachment"]["title_with_entities"].get("text")
                    except:
                        pass
                if not content:
                    try:
                        content = story["attached_story"]['message']['text']
                    except:
                        content = ""
                d_url = s["comet_sections"]["content"]["story"].get('wwwURL')
                uname = s["comet_sections"]["content"]["story"]['actors'][0].get('name')
                uid = s["comet_sections"]["content"]["story"]['actors'][0].get("id")
                profile_url = s["comet_sections"]["content"]["story"]['actors'][0].get("url")
                attached_story = s["comet_sections"]["content"]["story"].get('attached_story')
                is_origin = "转发" if attached_story else "原创"
                like_count = \
                    s["comet_sections"]["feedback"]["story"]["story_ufi_container"]["story"]["feedback_context"][
                        "feedback_target_with_context"]["comet_ufi_summary_and_actions_renderer"]["feedback"][
                        "reaction_count"]["count"]
                share_count = \
                    s["comet_sections"]["feedback"]["story"]["story_ufi_container"]["story"]["feedback_context"][
                        "feedback_target_with_context"]["comet_ufi_summary_and_actions_renderer"]["feedback"][
                        "share_count"]["count"]
                total_comment_count = \
                    s["comet_sections"]["feedback"]["story"]["story_ufi_container"]["story"]["feedback_context"][
                        "feedback_target_with_context"]["comet_ufi_summary_and_actions_renderer"]["feedback"][
                        "comment_rendering_instance"]["comments"]["total_count"]
                try:
                    video_view_count = \
                        s["comet_sections"]["feedback"]["story"]["story_ufi_container"]["story"]["feedback_context"][
                            "feedback_target_with_context"]["comet_ufi_summary_and_actions_renderer"]["feedback"][
                            "video_view_count"]
                    if not video_view_count:
                        video_view_count = 0
                except:
                    video_view_count = 0
                publish_time = 0
                try:
                    metadata = s["comet_sections"]["context_layout"]["story"]["comet_sections"]["metadata"]
                    for m in metadata:
                        creation_time = m.get("story", {}).get("creation_time")
                        if creation_time:
                            publish_time = self.transfromTime(creation_time)
                            break
                except:
                    try:
                        metadata = s["comet_sections"]["content"]["story"]["comet_sections"]["context_layout"]["story"][
                            "comet_sections"]["metadata"]
                        for m in metadata:
                            creation_time = m.get("story", {}).get("creation_time")
                            if creation_time:
                                publish_time = self.transfromTime(creation_time)
                                break
                    except:
                        # print([edge])
                        pass
                item = {
                    "post_id": post_id,
                    "comment_id": comment_id,
                    "发布时间": publish_time,
                    "文本": content,
                    "用户名": uname,
                    "账号主页链接": profile_url,
                    "用户id": uid,
                    "点赞数": like_count,
                    "转发数": share_count,
                    "评论数": total_comment_count,
                    "视频播放数": video_view_count,
                    "帖子链接": d_url,
                    "是否原创": is_origin,
                    "关键词": keyword,
                }
                self.data_count +=1
                print((self.data_count,item))
                resultList.append(item)
            except Exception as e:
                print("解析异常：",e)
                print("异常数据：",edge)
        if resultList:
            self.save_data(resultList)# 保存结果
    #数据保存
    def save_data(self, resultList):# 将数据保存为 CSV 文件
        self.saveFileName = "facebook数据"
        if resultList:
            df = pd.DataFrame(resultList)
            if not os.path.exists(f'{self.saveFileName}.csv'):
                df.to_csv(f'{self.saveFileName}.csv', index=False, mode='a', encoding="utf_8_sig")
            else:
                df.to_csv(f'{self.saveFileName}.csv', index=False, mode='a', encoding="utf_8_sig",
                          header=False)
            print("保存成功")
            
    def run(self,keyword,end_cursor,page):
        has_next_page = True
        while has_next_page:
            print("正在采集第：",page,"页"," end_cursor：",end_cursor)
            self.get_data(keyword, cursor=end_cursor)
            text = self.get()
            # print(text)
            if 'Rate limit exceeded' in text:
                print("请求限制中...")
                break
            if "errorSummary" in text or "errorDescription" in text:
                print([text])
                break
            else:
                data_str = text.split("\n")[0]
                # print([data_str])
                try:
                    data_json = json.loads(data_str)
                except Exception as e:
                    if "list index out of range" in str(e):
                        break
                    print(f"第一次json.loads数据异常，尝试第二次：{e}")
                    data_json = json.loads(text)
                try:
                    edges = data_json["data"]["serpResponse"]["results"]["edges"]
                    end_cursor = data_json["data"]["serpResponse"]["results"]["page_info"]["end_cursor"]
                    has_next_page = data_json["data"]["serpResponse"]["results"]["page_info"]["has_next_page"]
                    if not has_next_page:
                        break
                    if edges:
                        self.parse_data(keyword, edges)
                        page += 1
                    else:
                        has_next_page = False
                except Exception as e:
                    print(f"第一次解析数据异常：{e}")

    def read_params_init(self):
        if not os.path.exists('初始化参数.txt'):
            self.get_init_params()
        else:
            with open('初始化参数.txt', encoding='utf-8') as f:
                self.fb_dtsg, self.token = f.read().split("------")
 
    def main(self,start_day, end_day):
        self.start_day = start_day
        self.end_day = end_day
        keywords = ["Scam", "Cheating", "Fraud", "欺騙", "行騙", "詐騙", "詐欺", "電騙", "騙徒", "電詐", "騙錢","呃人", "呃錢", "電話騙案", "網上騙案", "網上呃錢", "網上詐騙", "騙徒手法層出不窮", "電郵騙案", "網上情緣騙案", "交友 app 騙案", "facebook 騙案"]
        for word in keywords:
            self.seachKeyWord = word
            self.run(word,"-1",1)



    def save_timestamp_to_file(self, timestamp, file_name):
        with open(file_name, "w", encoding="utf-8") as file:
            file.write(str(timestamp))

    # 读取时间戳
    def read_timestamp_from_file(self, file_name):
        try:
            with open(file_name, "r", encoding="utf-8") as file:
                return int(file.read().strip())  # 转换为整数时间戳
        except (FileNotFoundError, ValueError):
            return None


# 主程序
if __name__ == '__main__':
    # 读取 Cookie
        # with open('/Users/chenchen/Desktop/facebook_data/cookies.txt', encoding='utf-8') as f:
    with open('/Users/chenchen/Desktop/facebook_data/cookies.txt', encoding='utf-8') as f:
        cookie_str_list = [i.strip() for i in f.readlines() if i.strip() != ""]
    cookie_str = cookie_str_list[0]
    print(f"读取的 Cookie: {cookie_str}")

# 获取或初始化时间范围
    current_timestamp = int(datetime.now().timestamp())  # 当前时间戳
    end_day = datetime.fromtimestamp(current_timestamp).strftime("%Y-%m-%d")  # 结束日期
    timestamp_file = "last_timestamp.txt"

    # 读取上次时间戳
    try:
        last_timestamp = fbw.read_timestamp_from_file(timestamp_file)
    except NameError:
        print("read_timestamp_from_file 函数未定义，请检查代码。")
        exit(1)

    if last_timestamp:
        print(f"上次记录的时间戳：{last_timestamp}")
        print(f"对应的日期：{datetime.fromtimestamp(last_timestamp).strftime('%Y-%m-%d %H:%M:%S')}")
        start_day = datetime.fromtimestamp(last_timestamp).strftime("%Y-%m-%d")
    else:
        start_day = input("如果是第一次运行，请指定开始时间: i.e. '2024-01-01': ")
        print(f"你输入了：{start_day}")
        print("程序继续运行...")

    # 实例化类
    fbw = FaceBookKeyWord(cookie_str)
    # 保存当前时间戳
    try:
        fbw.save_timestamp_to_file(current_timestamp, timestamp_file)
        print(f"已保存当前时间戳：{current_timestamp}")
    except AttributeError as e:
        print(f"保存时间戳时发生错误: {e}")
        exit(1)

  
    fbw.read_params_init()
    fbw.main(2024-12-14,2024-12-14)

 