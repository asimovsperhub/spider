# coding=utf-8
import csv
import json

import requests
from fake_useragent import UserAgent
from lxml import etree
import time
from Crypto.Cipher import AES
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import algorithms
from binascii import b2a_hex, a2b_hex
import base64


def pkcs7_padding(data):
    if not isinstance(data, bytes):
        data = data.encode()

    padder = padding.PKCS7(algorithms.AES.block_size).padder()

    padded_data = padder.update(data) + padder.finalize()

    return padded_data


def encrypt(text, password):
    cryptor = AES.new(password, AES.MODE_CBC, password)
    text = text.encode('utf-8')

    text = pkcs7_padding(text)

    ciphertext = cryptor.encrypt(text)

    return base64.encodebytes(ciphertext).decode('utf8').strip().replace('\n', '')


class Search(object):

    def __init__(self):
        self.headers = {
            'User-Agent': str(UserAgent(verify_ssl=False).random)
        }
        self.dgtle_search = "https://www.dgtle.com/search/user?search_word=%s"
        self.gelonghui_search = "https://www.gelonghui.com/api/search/user?keyword=%s&count=20&page=1"
        self.oppo_search = "https://www.oppo.cn/search-member?keyword=%s&page=%s"
        self.wfdata_search = "https://api.wfdata.club/v1/search/userList?keyword=%s&pageCount=20&page=1"
        self.keladata = []
        self.kela_search = "https://www.hongdoufm.com/aboutus/serach/kw/%s"

    def dgtle(self, name):
        search_user = []
        url = self.dgtle_search % name
        rep = requests.get(url, self.headers)
        datalist = json.loads(rep.text).get("data").get("dataList")
        for data in datalist:
            id = data.get("id")
            username = data.get("username")
            url = "https://www.dgtle.com/user?uid=%s" % id
            search_user.append((username, url))
        total = len(search_user)
        return total, search_user

    def gelonghui(self, name):
        search_user = []
        url = self.gelonghui_search % name
        rep = requests.get(url, self.headers)
        search_count = json.loads(rep.text).get("result").get("totalCount")
        if search_count > 0:
            all_data_url = url.split("&")[0] + "&count=%s&page=1" % search_count
            rep_ = requests.get(all_data_url, self.headers)
            data = json.loads(rep_.text).get("result").get("userList")
            for data_ in data:
                userid = data_.get("userId")
                username = data_.get("username")
                user_info = "https://www.gelonghui.com/user/%s" % userid
                search_user.append((username, user_info))
            total = len(search_user)
            return total, search_user
        return 0, None

    def oppo(self, name):
        search_user = []
        url = self.oppo_search % (name, 1)
        rep = requests.get(url, self.headers)
        # rep.encoding="utf-8"
        root = etree.HTML(rep.text)
        # 至少一个div用户信息
        user_list = root.xpath('/html/body/div[1]/div[4]/div')
        if user_list:
            offset_list = root.xpath('/html/body/div[1]/div[4]/div[21]/p/span//text()')
            if offset_list:
                max = offset_list[-2].replace("第", "").replace("页", "")
                if int(max) > 0:
                    for offset in range(2, int(max) + 1):
                        url = self.oppo_search % (name, offset)
                        rep_ = requests.get(url, self.headers)
                        root_ = etree.HTML(rep_.text)
                        user_info_list = root_.xpath('/html/body/div[1]/div[4]/div')
                        for user in user_info_list:
                            if user.xpath('./div/div//@href'):
                                url = "https://www.oppo.cn" + user.xpath('./div/div//@href')[0]
                                username = "".join(user.xpath('./div/div//text()')).split("\n")[2].replace(" ", "")
                                search_user.append((username, url))
            user_info_list = root.xpath('/html/body/div[1]/div[4]/div')
            for user in user_info_list:
                if user.xpath('./div/div//@href'):
                    url = "https://www.oppo.cn" + user.xpath('./div/div//@href')[0]
                    username = "".join(user.xpath('./div/div//text()')).split("\n")[2].replace(" ", "")
                    search_user.append((username, url))
            return len(search_user), search_user
        return 0, []

    def wfdata(self, name):
        search_user = []
        sign = b'2b7e151628aed2a6'
        url = self.wfdata_search % name
        # url=/v1/search/userList$time=1620388244990000000
        sign_url = "url=/v1/search/userList$time=%s" % (str(round(time.time() * 1000)) + "000000")
        self.headers["x-request-id"] = encrypt(sign_url, sign)
        self.headers['Connection'] = 'keep-alive'

        rep = requests.get(url=url, headers=self.headers)
        total = json.loads(rep.text).get("data").get("total")
        if total > 0:
            is_int = total / 20
            if isinstance(is_int, float):
                pages = int(is_int) + 2
            else:
                pages = is_int + 1
            for page in range(1, pages):
                url_ = "".join(url.split("&")[0]) + "&pageCount=20&page=%s" % page
                rep_ = requests.get(url=url_, headers=self.headers)
                dataList = json.loads(rep_.text).get("data").get("dataList")

                for user in dataList:
                    # print(user.get("userBaseInfo").get("userName"))
                    # print(user.get("userBaseInfo").get("userId"))
                    # if user.get("userBaseInfo"):
                    userid = user.get("userBaseInfo").get("userId")
                    username = user.get("userBaseInfo").get("userName")
                    url_ = "https://www.feng.com/user/%s/moments" % userid
                    search_user.append((username, url_))

            return len(search_user), search_user
        return 0, []

    def kela(self, name=None, next_url=None):
        if name:
            search_url = self.kela_search % name
        else:
            search_url = next_url
        req = requests.get(search_url, self.headers)
        root = etree.HTML(req.text)
        user_list = root.xpath("/html/body/div[2]/div/div[2]/div[1]/div[1]/div[2]/a")
        next_page = "/html/body/div[2]/div/div[2]/div[1]/div[2]/a[2]/@href"
        for user in user_list:
            username = user.xpath("./div/div[2]/div[1]/div/text()")
            user_url = user.xpath("./@href")
            if len(username) > 0 and len(user_url) > 0:
                user_url_ = "https://www.hongdoufm.com/" + user_url[0]
                self.keladata.append((username[0], user_url_))
        if len(root.xpath(next_page)) > 0 and root.xpath(next_page)[0] != 'javascript:void(0);':
            page_url = "https://www.hongdoufm.com/" + root.xpath(next_page)[0]
            self.kela(next_url=page_url)

        return len(self.keladata), self.keladata


class SearchGeneral(Search):

    def general(self, app_id, name):
        search_d = {
            "4": "self.dgtle(name)",
            "8": "self.oppo(name)",
            "17": "self.wfdata(name)",
            "20": "self.gelonghui(name)",
            "1": "self.kela(name=name)",
        }
        if search_d.get(str(app_id)):
            return eval(search_d.get(str(app_id)))
        return 0, []


if __name__ == '__main__':
    e = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ \t\n\r\x0b\x0c'
    z = "０１２３４５６７８９ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ｀－＝【】、；‘’，。／＼～！＠＃￥％…＆×（）—＋｛｝｜：“”《》？〈〉＜＞〔〕〖〗『』"
    c = "一丁七万丈三上下不与丐丑专且丕世丘丙业丛东丝丞丠丢两严丧丨个丫中丰串临丶丸丹为主丼丽举乂乃久么义之乌乍乎乏乐乒乓乔乖乘乙乜九也习乡书买乱乳乾了予争亊事二亍于亏云互亓五井亘亚些亡亢交亥亦产亨亩享京亭亮亲亳人亿什仁仂仃仄仅仆仇仈今介仍从仑仓仔仕他仗付仙仝仞仟仡代令以仨仪仫们仰仲件价仹任份仿企伊伍伏伐休众优伙会伞伟传伡伢伤伦伪伮伯估伲伴伶伸伺伻似伽佁佃但位低住佐佑体何佗佘余佚佛作佞佟你佣佤佥佧佩佬佯佰佲佳佴併佶佷佸佼使侃侄侈例侍侎侏侑侕侗供依侠侣侦侧侨侪侬侮侯侵便促俄俈俊俎俏俐俑俗俚保俞信俣俦俩俪俫俬俭修俯俱俸俺俾倍倒倔倘候倚倜借倡倢倦倨倩倪倬倶债倻值倾偀偃假偈偌偎偏偕做停健偲偶偷偻偿傀傅傍傎傢傣傥傧储催傲傻像僖僚僡僦僧僮僰僵僻億儆儋儒儡儫儿兀允元兄充兆先光克免兑兔兕兖党兜兢入內全八公六兮兰共关兴兵其具典兹养兼兽兿冀内冇冈冉册再冒冕冖冗写冚军农冠冢冥冧冬冭冯冰冲决况冶冷冻冼净凃凄准凇凉凋凌减凑凛凝几凡凤凫凭凯凰凳凶凸凹出击函凿刀刁刃分切刈刊刍刑划列刘则刚创初删判別刨利别刮到制刷券刹刺刻剀剁剂剃削剌前剐剑剔剖剡剤剥剧剩剪副割剿劈力劝办功加务劢劣劦动助努劫劬劭励劲劳劵劻劼势勃勇勉勊勋勍勐勒動勖勘勝募勤勰勳勺勾勿匀包匆匈匕化北匙匝匟匠匡匣匪匮匹区医匾匿十千卅升午卉半华协卑卒卓单卖南博卜卞卟占卡卢卤卦卧卫卯印危即却卵卷卸卻卿厂厄厅历厉压厌厍厕厘厚厝原厢厦厨厩厶去县叁参叄又叉及友双反发叒叔取受变叙叟叠叡口古句另叩只叫召叭叮可台叱史右叶号司叹叻叼叽吁吃各合吉吊同名后吏吐向吒吓吕吖吗君吞吟吠吡否吧吨吩含听吮启吱吲吴吵吸吹吻吼吾吿呀呃呆呈告呋呐呓呔呕呗员呜呢呤呦周呱呲味呵呷呼命咀咆咋和咎咏咔咕咖咙咚咛咡咤咥咧咨咩咪咫咬咭咯咱咲咳咸咻咽咿哀品哂哃哄哆哇哈哉哋哌响哎哑哒哔哗哙哚哞哟哥哦哧哨哩哪哭哮哲哵哺哼哿唆唇唉唐唑唛唢唤唧唬售唯唰唱唻唾啃啄商啉啊啕啜啟啡啤啥啦啧啪啫啬啰啶啷啸啻啼喀喂喃善喆喇喉喊喏喔喘喙喜喝喧喬喯喱喵営喷喹喻喽喾嗅嗒嗓嗖嗜嗡嗣嗤嗥嗦嗨嗪嗮嗯嗲嗳嗷嗽嘀嘉嘌嘎嘚嘛嘞嘟嘢嘤嘧嘲嘴嘶嘹嘻嘿噁噜噢器噪噬噶噻噼嚎嚒嚢嚣嚼囊囍囗四回囟因囡团団囤囧园囯困囱围囵囷囸固国图囿圃圆圈圌圏園土圣圧在圩圪圭地圳场圻圾址坂均坊坌坎坏坐坑块坚坛坝坞坟坠坡坣坤坦坨坩坪坭坯坲坳坶坷坻坼垂垃垄垅型垌垒垓垚垛垞垟垠垡垢垣垤垦垧垩垫垭垮垯垱垲垴垵垸垹垾埂埃埇埋埌城埏埔埕埗埚埝域埠埤埩埫埭埰埴培基埼埾堀堂堃堆堇堉堑堔堕堡堤堪堭堯堰堵堺堼塅塌塍塑塔塗塘塚塞塥填塬塱塾墀墁境墅墉墊墒墓増墘墙增墟墨墩墶墺墻壁壇壑壓壕壤士壬壮声売壳壶壹处夆备复夏夔夕外夙多夜够大天太夫夭央夯失头夷夸夹夺夼奁奂奇奈奉奋奎奏契奔奕奖套奘奚奠奢奥奭女奴奵奶她好如妃妆妇妈妊妍妒妖妗妙妞妡妤妥妨妩妫妮妯妲妳妹妻姆姊始姐姑姓委姗姚姜姝姣姥姨姬姮姹姻姿威娃娄娅娆娇娈娉娌娑娓娘娜娟娠娣娥娩娭娱娲娴娶娼婀婆婇婉婊婔婕婗婚婢婧婳婴婵婶婷婺婿媂媄媒媖媗媚媛媞媤媪媲媳嫁嫂嫌嫒嫖嫘嫚嫡嫣嫦嫩嫱嬉嬴嬿子孑孔孕孖字存孙孚孛孜孝孞孟孢季孤学孩孪孰孵孺孽宁它宅宇守安宋完宏宓宕宗官宙定宛宜宝实宠审客宣室宥宦宪宫宬宰害宴宵家宸容宽宾宿寀寂寄寅密寇富寐寒寓寔寖寝寞察寡寥寨寮寰寸对寺寻导寿封射将尉尊尌小少尓尔尕尖尘尚尝尤尥尧尨就尴尸尹尺尻尼尽尾尿局屁层居屈屉届屋屌屎屏屐屑展屛属屠履屬屯山屸屹屺屽屾屿岀岁岂岍岐岑岔岗岘岙岚岛岜岞岡岢岦岩岫岭岱岳岷岸岺岽岿峁峄峒峙峡峣峤峥峦峨峪峭峮峯峰峸峹峻崀崂崃崆崇崎崑崔崖崙崚崛崟崦崧崨崩崭崮崯崴崽嵇嵉嵊嵋嵌嵘嵚嵛嵩嶂嶓嶝嶶嶷嶺巅巍川州巡巢工左巧巨巩巫差巯己已巳巴巷巽巾巿币市布帅帆师希帏帐帑帕帖帘帚帛帜帝带帧席帮帱帷常帺帼帽幂幄幅幔幕幛幡幢干平年并幸幺幻幼幽广広庄庆庇床序庐库应底庖店庙庚府庞废庠庥度座庭庵庶康庸庹庾廉廊廒廓廖廛廪延廷廸建廿开异弃弄弈弊弋弍式弓引弗弘弛弟张弢弥弦弧弩弯弱弶弹强弼归当录彗彝形彤彦彧彩彪彬彭彰影彳役彻彼往征径待很徉律徍徎徐徒徕得徙徜御徨循微徳徵德徹徽心必忆忌忍忑忒志忘忙忝忞忟忠忧快忭忱念忻忽怀态怎怒怔怕怖怛怜思怠怡急性怨怩怪总怿恂恉恊恋恐恒恕恙恢恣恤恨恩恪恬恭息恰恳恵恶恺恽悃悄悈悉悌悍悒悔悟悠患悦您悫悬悯悱悲悴悸悼情惊惑惜惟惠惢惦惧惨惩惬惯惰想惶惹惺愁愈愉意愔愚感愢愣愧愫愽愿慇慈慊慌慎慑慕慠慢慧慨慰慷憔憧憨憩憬憶憾懂懊懋懒懿戈戊戋戌戍戎戏成我戒或戗战戚戛戟截戬戳戴户房所扁扇扉手才扎扑扒打托扛扞扣扦执扩扪扫扬扭扮扯扰扳扶批扼找承技抄抉把抑抒抓投抖抗折抚抛抟抠抡抢护报披抬抱抵抷抹抺抻押抽拂拄担拆拇拉拌拍拎拏拐拒拓拔拖拗拘拙拚招拜拝拟拢拣拥拦拧拨择括拭拯拱拳拴拷拸拼拽拾拿持挂指按挎挑挖挚挞挟挠挡挣挤挥挨挪挫振挲挹挺挼挽捅捆捉捌捍捎捏捐捕捞损捡换捣捧捭据捶捷捻掀掇授掉掌掏掐排掖掘掛掠採探掣接控推掩措掬掭掷掺揆揉描提插揖握揭援揸揽搀搁搂搅搌搏搓搔搜搞搪搬搭携搽摁摄摆摇摊摔摘摧摩摸摹摺撇撑撒撕撙撞撤撩撬播撮撰撵撷撸撼擀擂擅操擎擒擘擢擦攀攒攘支收攸改攻放政故效敉敌敏救敔敕敖教敛敝敞敢散敦敬数敲整敷文斋斌斐斑斓斗料斛斜斟斡斤斥斧斩断斯新方於施旁旃旅旆旋旌旎族旖旗无既日旦旧旨早旬旭旮旯旱旲旳时旷旸旺旻旼昀昂昆昇昉昊昌明昏易昔昕昙昜星映昡春昨昫昭是昱昴昵昶昷昼昽显晁晃晅晋晏晒晓晔晕晖晗晙晚晞晟晠晡晢晤晦晧晨晫普景晰晴晶晷智晾晿暂暄暇暑暖暗暘暠暧暨暮暴暹暻暾曈曌曙曜曝曦曰曲曳更曵曹曻曼曾替最月有朊朋服朐朔朕朗望朝期朦木未末本札术朱朴朵朸机朽杀杂权杆杈杉杍李杏材村杓杕杖杜杞束杠条来杨杩杪杭杯杰東杲杳杵杷杺杼松板极构枇枉枋枎析枓枕林枘枚果枝枞枢枣枥枧枪枫枭枯枰枱枳架枸枼柄柆柊柏某柑柒染柔柘柚柜柞柟柠柢查柬柯柱柳柴柵柸査柽柿栀栅标栈栉栊栋栌栎栏树栓栖栗栝校栢栩株栱栲栳样核根格栽栾桀桁桂桃桅框案桉桌桎桐桑桓桔桕桠桡桢档桤桥桦桧桨桩桫桭桴桶桷桹桾梁梅梆梓梗梢梦梧梨梭梯械梱梳梵梽梾检棉棋棍棐棒棓棕棘棚棠棣棨棪森棰棱棵棹棺椅椋植椎椒椤椭椰椴椹椽椿楀楂楒楔楗楚楝楞楠楣楥楦楫楬業楷楸楹楼楽榀概榃榄榆榈榉榑榔榕榛榜榞榧榨榫榭榮榴榷榻槃槊槌槍槎槐槛槟槭槲槽槿樊樋樑樘樟模樨横樯樱樵樽樾橄橇橐橖橘橙機橡橦橱橹橼檀檄檐檗檩檫檬檾櫃欄欐欠次欢欣欧欲欺款歁歆歇歈歉歌歘歙止正此步武歧歪死殉殊残殖殡殳段殷殿毁毂毅毋母每毑毒毓比毕毗毙毛毡毫毯氏氐民氓气氖氘氙氚氛氟氡氢氣氦氧氨氩氪氮氯氰水永氺氿汀汁求汇汉汊汌汎汏汐汕汖汗汛汜汝汞江池污汣汤汦汨汪汫汭汮汯汰汲汴汶汽汾沁沂沃沄沅沈沉沌沏沐沓沔沕沖沙沚沛沟没沣沤沥沦沧沨沩沪沫沬沭沮沱河沸油治沼沽沾沿泃泄泇泉泊泌泓泔法泖泗泛泞泠泡波泥注泪泫泮泯泰泱泳泵泷泸泺泻泼泽泾洁洄洇洊洋洎洒洗洙洛洝洞洢津洧洪洮洰洱洲洳洵洸洹洺活洼洽派流浅浆浇浈浉浊测济浏浐浑浒浓浔浙浚浜浠浡浣浤浥浦浩浪浮浯浲浴浵海浸涂涅消涉涌涎涑涓涔涕涛涝涞涟涠涡涣涤润涧涨涩涪涮涯液涵涸涿淀淂淄淅淆淇淋淌淏淑淓淕淖淘淙淝淞淠淡淤淦淩淫淬淮淯深淳混淸淹添淼渃清渉渊渋渌渍渎渐渑渔渖渗渚減渝渠渡渣渤渥渧温測渭港渱渲渴渶游渺渼湃湄湍湎湑湓湔湖湘湛湝湟湧湫湲湴湶湾湿溃溅溆溇溉溋溏源溙溜溟溢溥溧溪溯溱溴溶溹滁滂滃滅滆滇滈滋滌滏滑滓滔滕滗滘滙滚滞滟滠满滢滤滥滦滨滩滮滱滴漂漆漉漍漏漓演漕漖漠漩漪漫漭漮漯漱漳漾潆潇潋潍潓潘潜潞潠潢潦潭潮潺潼潽澂澄澈澉澌澍澎澔澗澜澡澣澥澧澲澳澴澹激濂濉濎濑濒濛濠濡濬濮濯瀍瀑瀚瀛瀜灃灌灏灜灝灞火灭灯灰灵灶灸灼灾灿炀炅炉炊炎炒炔炕炖炘炙炜炝炟炤炫炬炭炮炯炱炳炸点炻炼炽烁烂烃烈烊烔烘烙烛烜烟烤烦烧烨烩烫烬热烯烱烷烹烺烽焉焊焌焐焓焕焖焗焘焙焚焜焦焬焯焰焱然焺煅煊煋煌煎煜煞煤煦照煨煬煮煲煸煽煾熄熊熏熔熙熟熠熤熥熨熬熱熳熵熹熾燀燃燈燊燎燕燚燠燥燧燮燿爃爆爇爨爪爬爰爱爵父爷爸爹爻爽牁牂片版牌牒牙牛牟牠牡牢牦牧物牲牵特牺犀犁犇犍犟犬犯犴状犸犹狂狄狍狐狗狠狡狩独狭狮狱狸狼猇猊猎猕猗猛猜猩猪猫猬献猴猷猾猿獐獒獬獭玄率玉王玎玏玑玓玖玘玙玛玜玟玡玢玥玧玩玫玮环现玲玳玴玶玹玺玻玿珀珂珃珅珈珉珊珍珏珐珑珙珝珞珠珣珥珧珩珪班珮珰珲珵珷珹珺球琅理琇琉琊琋琍琎琏琐琚琛琢琥琦琨琩琪琬琮琯琰琳琴琵琶琸琻琼瑀瑁瑄瑅瑆瑊瑕瑗瑙瑚瑛瑜瑝瑞瑟瑢瑧瑭瑰瑶瑷瑺瑾璀璁璃璇璈璋璎璐璘璜璞璟璠璧璨環璱璿瓒瓘瓜瓠瓢瓣瓤瓦瓮瓯瓴瓶瓷瓿甁甄甑甘甙甚甜生甡產用甩甪甫甬甭甯田由甲申电男甸町画甽甾畅畈畋界畏畑畔留畜略畦番畯畲畴畸畹畾畿疃疆疋疌疍疏疑疔疗疙疝疣疤疫疮疯疱疲疵疹疼疾痂病症痒痔痕痘痛痞痣痤痧痫痰痴痹瘀瘘瘛瘟瘠瘢瘤瘦瘩瘪瘫瘾癀癌癜癞癣癫癸発登發白百皂的皆皇皈皋皎皑皓皕皖皙皮皱皿盂盅盆盈盉益盎盏盐监盒盔盖盗盘盛盜盟盤盥目盯盱盲直盷相盺盼盾省眉看眙真眠眩眬眯眶眷眸眺眼着睁睇睐睛睡睢督睦睫睹睿瞄瞌瞎瞒瞧瞩瞪瞬瞭瞰瞳瞹瞻瞿矗矛矜矞矢矣知矩矫短矮石矶矸矼矽矾矿砀码砂砌砍砑研砖砗砚砜砝砟砢砣砥砦砧砬砭砰砳破砵砷砸砹砺砻砼砾础硂硅硇硌硐硒硕硖硚硝硫硬确硷硼碁碇碉碌碍碎碑碗碘碚碛碟碣碧碰碱碲碳碴碶碹碾磁磅磉磊磋磐磙磡磨磬磲磴磷磺礁礅礌礠礡礳礴示礼礽社祀祁祈祉祎祐祖祙祚祛祜祝神祠祤祥票祭祯祷祸祺祼禀禁禄禅福禛禧禹禺离禽禾秀私秃秆秉秋种秏科秒秘秞租秣秤秦秧秩秭积称秸移秾稀程稍税稔稗稘稚稜稞稠稣種稳稷稻稼稽稿穆穑穗穴究穷穹空穿突窃窄窈窍窑窒窕窖窗窘窛窜窝窟窠窥窦窨窿立竑竔竖站竜竞竟章竢竣竤童竭端竹竺竿笃笆笈笋笏笑笔笕笙笛笠笤笥符笨笪第笮笳笺笼笾筀筆等筋筌筏筐筑筒答策筘筛筜筝筠筱筵筷筹筻筼签简箄箅箍箐箓箔箕算箝管箦箩箪箫箬箭箱箴箸篁篆篇篏篓篙篝篦篮篱篷篼篾簇簋簏簕簧簸簿籁籍米籴类籼籽粉粑粒粕粗粘粟粢粤粥粦粧粨粪粮粱粲粳粹粼粽精粿糁糊糍糕糖糙糜糟糠糯糸系糼紊紙素紡索紧紫紬累組絎絮絲絷綦網緑線緾縁縫總繁繕纂纠红纤约级纨纪纫纬纭纮纯纱纲纳纵纶纷纸纹纺纽纾线练组绅细织终绉绊绍绎经绑绒结绕绗绘给绚绛络绝绞统绠绡绢绣绥绦继绨绩绪绫续绮绯绰绱绲绳维绵绶绷绸综绽绿缀缂缃缅缆缇缈缉缌缎缑缓缔缕编缗缘缙缚缜缝缠缡缢缤缥缦缧缨缩缪缫缬缮缯缳缴缶缷缸缺罂罄罅罉罐网罕罗罘罚罟罡罢罩罪置署羁羊羌美羑羔羚羞羟羡羣群羧義羰羲羴羸羹羽羿翀翁翃翅翊翌翎翔翕翘翙翟翠翡翥翩翮翯翰翱翳翻翼翾耀老考者耆而耍耐耒耔耕耗耘耙耦耧耳耶耸耻耽耿聂聃聆聊聋职联聖聘聚聪聶聿肃肆肇肉肋肌肓肖肘肚肛肝肟肠股肢肤肥肩肪肮肯肱育肴肺肼肽肾肿胀胁胂胃胄胆背胍胎胖胚胜胞胡胤胥胧胨胪胫胭胰胱胲胳胴胶胸胺能脂脆脉脊脍脏脐脑脒脖脘脚脯脰脱脲脸脾脿腃腈腊腋腌腐腓腔腕腙腥腩腮腰腹腺腻腾腿膀膊膏膘膛膜膝膠膦膨膳膺臀臂臆臊臣臧自臬臭至致臻臼臾舁舂舅舆舌舍舒舔舜舞舟舣航舫般舯舰舱舵舶舷舸船舾艄艇艉艋艘艟艨艮良色艳艺艾节芃芈芊芋芍芎芏芐芑芒芗芘芙芜芝芠芡芥芦芨芩芪芫芬芭芮芯花芳芴芷芸芹芽芾苁苄苇苊苋苌苍苎苏苑苒苓苔苖苗苘苛苜苞苟苡苣若苦苫苯英苳苴苷苹苼苾茁茂范茄茅茆茉茌茎茏茗茚茛茜茝茧茨茫茬茭茯茱茳茴茵茶茸茹荀荃荆荇草荏荐荑荒荔荘荙荚荛荜荞荟荠荡荣荤荥荦荧荨荪荫荭药荷荸荻荼莅莆莉莊莎莒莓莘莛莜莞莠莨莩莪莫莰莱莲莳莴获莹莺莼莽菀菁菂菅菇菈菊菌菏菓菖菘菜菟菠菡菩菪華菱菲菻萁萂萃萄萌萍萏萘萜萝萤营萦萧萨萩萱落葆葑葓著葙葚葛葡董葩葫葬葭葱葳葵葶葸葺蒂蒄蒉蒋蒌蒎蒗蒙蒜蒟蒡蒯蒲蒸蒻蒽蒿蓁蓄蓆蓉蓊蓑蓓蓖蓝蓟蓥蓦蓬蓼蓿蔄蔓蔗蔚蔡蔬蔵蔷蔸蔺蔻蔼蔽蕂蕃蕈蕉蕊蕗蕙蕞蕤蕥蕨蕭蕲蕴蕾薁薄薇薏薛薡薪薮薯薰薹藁藉藍藏藐藓藕藜藠藤藩藻藿蘅蘑蘖蘭蘸蘼虅虎虏虐虑虓虔處虚虞虢虫虬虱虸虹虻虽虾蚀蚁蚂蚄蚊蚌蚍蚓蚕蚝蚣蚤蚧蚨蚩蚪蚬蚯蚶蛀蛄蛆蛇蛋蛎蛏蛐蛙蛛蛟蛤蛭蛮蛰蛲蛳蛴蛹蛾蜀蜂蜃蜇蜈蜉蜊蜍蜒蜓蜕蜗蜘蜚蜜蜡蜢蜥蜱蜴蜻蜿蝇蝈蝉蝌蝎蝗蝙蝠蝣蝥蝮蝰蝴蝶螂螃融螟螨螬螭螯螳螺蟀蟆蟋蟑蟒蟠蟹蟾蠊蠓蠕蠡血行衍衎衔街衙衡衢衣补表衫衬衮衰衲衷衽衾衿袁袂袄袅袆袈袋袍袏袒袔袖袜袤袪被袭袱袼裁裂装裏裔裕裘裙裝裟裡裢裤裥裨裱裳裴裸裹裾褀褂褆褐褒褔褚褥褪襄襟西要覃覆见观规觅视览觉觊觐角觚觞解触言設訾詢試話詹誉誊誓調謇警護讀讃计订认讨让讫训议讯记讲讳讴讶讷许论讼讽设访诀证诂诃评识诈诉诊词诏译试诗诘诚诛诜话诞诟诠诡询诣诤该详诩诫语误诰诱诲说诵诶请诸诺读课谁调谅谆谈谊谋谌谍谏谐谒谓谕谘谙谚谛谜谟谢谣谥谦谧谨谬谭谯谱谴谷豁豆豉豊豌豐豚象豪豫豸豹豺貂貅貉貌貔貘財貮貳貹資賨質賽贝贞负贡财责贤败账货质贩贪贫贬购贮贯贰贱贲贴贵贶贷贸费贺贻贼贾贿赀赁赃资赉赊赋赌赎赏赐赑赓赔赖赘赚赛赜赞赟赠赡赢赣赤赫赭走赴赵赶起趁超越趋趟趣足趴趵趸趾跃跆跋跌跑距跞跟跤跨跪跬路跳践跷跻踊踌踏踝踞踢踩踪踵踹蹄蹈蹊蹦蹬蹭蹲躁身躬躯躺車车轧轨轩转轭轮软轰轱轲轴轶轸轹轺轻轼载轾轿辂较辅辆辇辈辉辊辋辐辑输辕辖辗辘辙辚辛辜辞辟辣辦辨辩辫辰辱边辽达迁迂迅过迈迎运近迓返还这进远违连迟迢迤迦迩迪迫迭述迳迴迷迹追退送适逃逄逅逆选逊逍透逐逑递途逖逗通逛逝逞速造逢逦逵逸逻逼逾遁遂遄遇遊遍遏遐遒道遗遛遣遥遨適遭遮遵避邀邂邃邈邊邑邓邕邗邛邝邡邢那邦邨邪邬邮邯邰邱邳邴邵邸邹邺邻郁郃郄郅郊郎郏郐郑郓郜郝郞郡郢郦郧部郫郭郯郴郸都郾鄂鄄鄙鄞鄠鄢鄣鄯鄱酆酉酊酋酌配酐酒酚酝酞酡酢酣酥酩酪酫酬酮酯酰酱酵酶酷酸酿醅醇醉醋醌醍醐醒醚醛醪醫醯醴醵釆采釉释里重野量金釘釜釨釹鈉鈊鈜鈤鈷鉋鉎鉑鉓鉚鉩鉮鉰鉴鉻銍銘銠銮銲銷鋁鋆鋈鋐錂錄錡錱錾鍠鍹鎏鎓鎧鏇鏊鏖鏻鐏鑫钅钆钇针钉钊钌钎钏钐钒钓钕钖钗钘钙钚钛钜钝钞钟钠钡钢钣钤钥钦钧钨钩钪钫钬钭钮钯钰钱钲钳钴钵钶钸钹钺钻钼钽钾钿铀铁铂铃铄铅铆铈铉铊铋铌铍铎铐铑铒铔铕铖铛铜铝铟铠铡铢铣铤铧铨铪铫铬铭铮铯铰铱铲铵银铷铸铺铼铽链铿销锁锂锃锄锅锆锇锈锉锋锌锍锎锏锐锑锒锕锖锗锘错锚锜锝锞锟锠锡锢锣锤锥锦锨锭键锯锰锱锲锳锴锵锶锷锹锺锻锽镀镁镂镆镇镈镉镊镌镍镏镐镑镒镓镔镕镖镗镘镙镚镛镜镝镡镤镥镦镧镨镪镫镭镯镰镱镲镶长門门闪闫闭问闯闰闱闲闳间闵闶闷闸闹闺闻闼闽闾闿阀阁阂阅阆阈阉阊阎阐阑阔阖阗阙阚阜队阡阪阮防阳阴阵阶阻阿陀陂附际陆陇陈陉陋陌降限陕陛陞陟陡院除陨险陪陲陵陶陷陽隅隆隈隋隍階随隐隔隗隘隙障隧隰隶隹隼隽难雀雁雄雅集雇雉雌雍雎雏雒雕雙雨雩雪雯雲雳零雷雹電雾需霁霄霆震霈霉霍霏霓霖霜霞霭露霳霸霹霾青靓靖静靛非靠靡面靥革靯靳靴靶靼鞅鞋鞍鞑鞘鞠鞣鞭韦韧韩韪韫韬韭音韵韶韸頔頣顕页顶顷顸项顺须顼顽顾顿颀颁颂预颅领颇颈颉颌颍颐频颓颖颗题颙颚颛颜额颠颡颢颤颦風风飏飒飓飘飙飚飞食飧飨餍餐餮饕饥饨饪饭饮饯饰饱饲饴饵饶饷饺饼饽饿馀馃馄馅馆馈馋馍馏馒馓馔馕首馗香馥馨馫騄驣驫马驭驮驯驰驱驳驴驶驷驸驹驻驼驽驾驿骀骁骂骄骅骆骇骈骉骊骋验骏骐骑骓骗骙骚骛骜骝骞骠骡骢骤骥骧骨骰骼髋髓高髙鬃鬐鬓鬲鬼魁魂魄魅魏魔魴鮀鮰鱻鱼鱿鲀鲁鲂鲃鲅鲆鲈鲊鲌鲍鲎鲐鲑鲒鲚鲜鲞鲟鲡鲢鲤鲥鲨鲫鲭鲯鲱鲲鲴鲵鲶鲸鲽鳄鳅鳇鳊鳌鳍鳎鳕鳖鳗鳙鳝鳞鳟鶱鸟鸠鸡鸢鸣鸥鸦鸩鸪鸫鸬鸭鸯鸰鸳鸵鸶鸷鸸鸽鸾鸿鹂鹃鹄鹅鹇鹉鹊鹋鹌鹍鹏鹑鹖鹗鹚鹞鹤鹦鹧鹫鹭鹰鹳鹿麂麇麋麒麓麝麟麥麦麸麻麽麾黃黄黉黍黎黏黑黒黔默黛點黟黧黯鼋鼎鼐鼓鼠鼬鼹鼻鼾齐齿龄龅龆龈龘龙龚龟"
    s = SearchGeneral()
    s_time = time.time()
    file = open("/home/root1/NetLetter/NetLetter/csv_data/16_kela.csv", 'a+', newline='', encoding='utf-8')
    fieldnames = ['url', 'username']
    writer = csv.DictWriter(f=file, fieldnames=fieldnames)
    writer.writeheader()
    for i in e + z + c:
        if i != " ":
            # print(i)
            _, data = s.general("1", i)
            for d in data:
                if d:
                    # print(d)
                    writer.writerow({"url": d[1], "username": d[0]})
    file.close()
    e_time = time.time()
    print(e_time - s_time)
