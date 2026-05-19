"""Mock news data for Vision Lens — 3 realistic Chinese news scenarios.

Each scenario includes multi-source data: official, we-media, and social media comments.
Designed to simulate the conflicting narratives the multi-agent debate system is built to untangle.
"""

from typing import Optional

# ============================================================
# Scenario 1: EV Crash & Fire Controversy
# ============================================================

SCENARIO_EV_CRASH = {
    "topic": "某品牌新能源车高速碰撞后起火，车门无法打开致1死2伤",
    "summary_5w1h": {
        "who": "一辆XX品牌Model S型新能源轿车，驾驶员王某(男，35岁)、乘客李某(女，32岁)、乘客张某(男，8岁)",
        "what": "车辆在高速行驶中碰撞护栏后起火燃烧，主驾车门无法打开，造成1死(张某)2伤",
        "when": "2025年3月15日凌晨2:30",
        "where": "G50沪渝高速湖北宜昌段K1234+500处",
        "why": "初步调查指向车辆碰撞后电池包热失控，但具体起火原因及车门锁死原因仍在调查中",
        "how": "车辆以约110km/h撞击护栏→电池包受损→3秒内起火→主驾车门电子锁失效→路人破窗救出2人",
    },
    "official": {
        "source": "湖北省交警总队 / 应急管理部",
        "statements": [
            {
                "text": "事故原因正在调查中，初步判定车辆碰撞护栏导致电池受损引发火灾。涉事车辆已送检，将委托第三方机构对电池安全性和车门锁止机构进行检测。",
                "evidence": ["事故现场照片(官方发布3张)", "高速监控视频片段(已封存)"],
                "reliability": 0.9,
            },
            {
                "text": "经初步调查，事故车辆在碰撞前以110km/h速度行驶，未发现驾驶员酒驾、毒驾。碰撞后安全气囊正常弹出。",
                "evidence": ["行车记录仪数据", "驾驶员血检报告"],
                "reliability": 0.95,
            },
        ],
    },
    "we_media": [
        {
            "source": "汽车独立评论人 @极速论车 (微博粉丝280万)",
            "text": "XX品牌此前就曾因电池安全问题在北美被调查，这次事故再次暴露其电池管理系统(BMS)的设计缺陷。碰撞后3秒即起火，说明电池包的热失控防护形同虚设。更可怕的是车门电子锁在断电后无法机械开启，这简直是杀人设计！",
            "evidence": ["引用2023年北美NHTSA调查报告", "同型号车辆BMS拆解视频"],
            "url": "https://weibo.com/u/example_speed_critic",
            "emotional_tone": "angry",
            "possible_interest": "该博主长期批评XX品牌，曾接受竞品品牌投放广告",
        },
        {
            "source": "科技媒体 @电动星球 (微信公众号)",
            "text": "客观来说，110km/h碰撞护栏的工况已经远超国家标准(国标要求50km/h侧碰)。任何电动车在这种极端碰撞下都有起火风险。不要把个案无限放大成品牌危机。关键要看第三方检测报告出来后的结论。",
            "evidence": ["引用C-NCAP碰撞标准", "对比特斯拉、蔚来类似事故数据"],
            "url": "https://mp.weixin.qq.com/s/example_ev_planet",
            "emotional_tone": "neutral",
            "possible_interest": "该媒体以电动车行业深度报道为主，未发现与特定品牌的利益关系",
        },
        {
            "source": "短视频博主 @老司机说车 (抖音粉丝560万)",
            "text": "现场视频太惨了！奉劝大家千万别买电车，油车撞了起码不会秒变火葬场。为了省那点油钱把命搭上不值！已有多位车主联系我反映该品牌门把手冬天冻住打不开的问题。",
            "evidence": ["网友投稿的门把手故障视频(5段)", "事故现场路人拍摄视频"],
            "emotional_tone": "fearful",
            "possible_interest": "该博主从事二手车买卖，以收售燃油车为主",
        },
    ],
    "social_media": {
        "sentiment_stats": {"angry": 0.42, "fearful": 0.28, "neutral": 0.15, "supportive": 0.10, "sarcastic": 0.05},
        "representative_comments": [
            {
                "user": "@京城刘大律",
                "text": '作为律师，提醒大家：电子门锁在碰撞后无法机械开启可能构成产品缺陷，家属可以依据《产品质量法》第46条提起诉讼。关键在于证明“不合理危险”的存在。',
                "emotion": "neutral",
                "likes": 32400,
            },
            {
                "user": "@吃瓜不嫌事大",
                "text": '前排提醒：这品牌去年才因为“刹车失灵”上过热搜，公关费怕是又要破亿了[doge]',
                "emotion": "sarcastic",
                "likes": 18900,
            },
            {
                "user": "@沉默的大多数",
                "text": "我朋友的同事就是开这车的，他说车友群里都在删聊天记录了，你们细品。",
                "emotion": "fearful",
                "likes": 8700,
            },
            {
                "user": "@理性看世界",
                "text": "等等看第三方检测报告吧，现在下定论太早。每次出事故都是先骂再说，反转了多少次了。",
                "emotion": "neutral",
                "likes": 12000,
            },
            {
                "user": "@电车死忠粉",
                "text": "我开了3年XX品牌，从来没出过问题。这次明显是驾驶员疲劳驾驶，撞护栏的锅也要甩给车？",
                "emotion": "supportive",
                "likes": 5600,
            },
        ],
    },
}

# ============================================================
# Scenario 2: Social Hot-Button Reversal — "Donation Fraud"
# ============================================================

SCENARIO_DONATION = {
    "topic": "女子网络筹款50万称女儿患白血病，被曝家有3套房后剧情多次反转",
    "summary_5w1h": {
        "who": "筹款人赵某(女，29岁，全职主妇)、其丈夫钱某(35岁，企业中层)、女儿(4岁，确实被确诊为急性淋巴细胞白血病)",
        "what": "赵某在水滴筹发起50万元筹款，声称家庭困难无力承担医药费。后有网友爆料其名下有3套房产，引发舆论风暴。随后又出现新证据表明其中2套房产已变卖用于前期治疗。",
        "when": "筹款发起于2025年1月10日，爆料出现在1月15日，反转出现在1月18日",
        "where": "水滴筹平台 / 微博 / 抖音",
        "why": "核心争议：筹款人在有能力自行承担部分费用的情况下发起筹款是否构成欺诈？已变卖房产但未及时更新家庭资产信息的披露义务边界在哪里？",
        "how": "发起筹款→媒体转载扩大影响→网友人肉搜索扒出房产信息→舆论反转谴责→更多证据浮出→部分反转→持续争议中",
    },
    "official": {
        "source": "水滴筹平台 / 就诊医院 / 当地民政部门",
        "statements": [
            {
                "text": "经核查，筹款人赵某的女儿确于2024年12月在北京儿童医院确诊为急性淋巴细胞白血病(ALL-L2型)，情况属实。第一期治疗费用预计35万元，目前已花费约28万元。",
                "evidence": ["医院诊断证明(平台已核验)", "费用清单(部分)"],
                "reliability": 0.95,
            },
            {
                "text": "平台规则要求发起人如实披露家庭资产状况。赵某在发起时申报的房产数量为1套(自住)，未披露另外2套房产。平台已启动核查程序，筹款资金目前处于冻结状态。",
                "evidence": ["平台筹款协议", "赵某提交的资产申报表"],
                "reliability": 0.9,
            },
            {
                "text": "当地民政部门证实，赵某家庭未申请低保或其他救助，其丈夫钱某所在公司(某互联网企业)已为其提供了10万元员工大病互助金。",
                "evidence": ["民政系统查询记录", "企业互助金发放凭证"],
                "reliability": 0.9,
            },
        ],
    },
    "we_media": [
        {
            "source": "深度报道媒体 @北青深一度",
            "text": "记者实地走访发现，赵某名下3套房产中，1套为自住(约90平米)，另外2套(分别约60平和45平)确实已于2024年12月以急售方式卖出，成交价合计约180万，低于市场价约30万。卖房款中约150万已用于支付前期检查和治疗费用(含骨髓配型)。赵某未更新申报信息属于违规，但'有3套房还诈捐'的说法与事实有较大出入。",
            "evidence": ["房产交易合同照片", "银行流水截图(部分)", "医院缴费记录", "邻居采访录音"],
            "emotional_tone": "neutral",
            "possible_interest": "该媒体以深度事实核查见长，公信力较高",
        },
        {
            "source": "自媒体大V @热点追缉令 (微博粉丝450万)",
            "text": "有3套房还众筹？这跟讹诈有什么区别！即使卖了2套，不还有1套吗？凭什么让月薪5000的打工人给住90平大房子的人捐款？水滴筹的审核形同虚设！建议直接封杀这个平台！",
            "evidence": ["房产查档截图(3套房)", "未提及已变卖的事实"],
            "emotional_tone": "angry",
            "possible_interest": "该账号以情绪化爆料为主，追求流量变现，有多次被指断章取义的历史",
        },
        {
            "source": "财经博主 @商业望远镜",
            "text": "从理性的角度分析：白血病治疗总费用一般在50-100万之间(含骨髓移植)。这个家庭年收入约40万(丈夫工资)，卖房获得180万，扣除前期28万，理论上仍有约200万资产。发起50万筹款至少存在信息披露不完整的问题。但'诈捐'需要证明主观恶意，这个很难认定。",
            "evidence": ["国内白血病治疗费用统计", "家庭收入推算(基于行业数据)"],
            "emotional_tone": "neutral",
            "possible_interest": "商业分析类博主，无明显利益相关",
        },
    ],
    "social_media": {
        "sentiment_stats": {"angry": 0.38, "sympathetic": 0.22, "neutral": 0.18, "sarcastic": 0.12, "supportive": 0.10},
        "representative_comments": [
            {
                "user": "@某三甲医院血液科医生",
                "text": "ALL-L2型在儿童中治愈率可达85%以上，但前提是有足够的资金支持规范治疗。这个家庭确实遭遇了不幸，但信息披露不完整确实会影响捐赠人的判断。",
                "emotion": "neutral",
                "likes": 28500,
            },
            {
                "user": "@人间不值得",
                "text": "经典剧本：第一天感动落泪到处转发 → 第二天发现不对劲开始质疑 → 第三天全面反转开骂 → 第四天发现好像也没那么坏 → 第五天新的热点来了无人关心。",
                "emotion": "sarcastic",
                "likes": 45200,
            },
            {
                "user": "@保险代理人小李",
                "text": "说句不好听的，年收入40万的家庭不买重疾险，出事就众筹，本质上就是风险转嫁。我们的捐款实际上在替他们交'保费'。",
                "emotion": "angry",
                "likes": 19800,
            },
            {
                "user": "@白血病患儿家属",
                "text": "我孩子也在治疗中，我知道那种绝望。卖了房子还不够是很正常的，骨髓移植光进仓就要30万。大家嘴下留德吧，孩子是无辜的。",
                "emotion": "sympathetic",
                "likes": 22300,
            },
            {
                "user": "@理中客一号",
                "text": "整理一下时间线：1月10日发起筹款→15日被爆房产→16日赵某发声明称已卖房→18日记者核实属实。问题在于筹款时未更新信息，但是否有意隐瞒还需要平台调查。先别急着站队，等最终结论。",
                "emotion": "neutral",
                "likes": 35600,
            },
        ],
    },
}

# ============================================================
# Scenario 3: AI-Generated Fake News
# ============================================================

SCENARIO_AI_FAKE = {
    "topic": "某地发生'AI伪造官方文件'事件：网传'市政府搬迁通知'被证实为AI生成",
    "summary_5w1h": {
        "who": "未知发布者(IP追踪指向境外服务器)；涉及城市为江苏省某地级市",
        "what": "一份声称'市政府将于2025年6月搬迁至高新区'的红头文件在网上流传，格式逼真，印章完整。后被证实为AI生成伪造文件。当地多家房产中介借机炒作高新区房价。",
        "when": "文件首次出现于2025年4月2日，政府辟谣于4月3日，造谣者身份仍在追查中",
        "where": "微信朋友圈、微信群、抖音、小红书",
        "why": "推测动机：炒高高新区房价获利。文件出现后24小时内，高新区多个楼盘出现抢购潮，4月3日政府辟谣后部分购房者要求退房。",
        "how": "使用AI文本生成+图像生成工具伪造红头文件→通过房产中介群扩散→自媒体跟进炒作→政府紧急辟谣→公安机关立案侦查",
    },
    "official": {
        "source": "市政府新闻办 / 市公安局网安支队",
        "statements": [
            {
                "text": "网传'市政府搬迁通知'系伪造文件，市政府无任何搬迁计划。该文件使用了AI技术仿造公文格式和政府印章，目前公安机关已立案侦查。请广大市民不信谣、不传谣。",
                "evidence": ["官方辟谣公告(政府官网)", "新闻发布会视频"],
                "reliability": 0.98,
            },
            {
                "text": "经技术鉴定，该文件存在多处AI生成特征：印章编号与真实编号字体不一致；正文中存在典型的LLM生成的重复句式；红头文件编号格式与真实公文规范有3处不符。",
                "evidence": ["网安支队技术鉴定报告摘要", "真伪文件对比图"],
                "reliability": 0.95,
            },
            {
                "text": "已初步锁定传播源头为某房产中介公司员工群。4月2日下午，有人将伪造文件以PDF形式发送至该群，群内多名中介人员在未核实的情况下转发至朋友圈和客户群。",
                "evidence": ["聊天记录截图", "传播路径技术分析"],
                "reliability": 0.85,
            },
        ],
    },
    "we_media": [
        {
            "source": "科技博主 @AI前沿观察 (知乎/微博)",
            "text": "这次事件给所有人敲响警钟：AI生成的红头文件已经可以以假乱真。普通民众根本分不清真假。我测试了用Claude+Midjourney生成类似文件，10分钟就能做出来。这还只是开始，以后AI伪造的政府公告、公司财报、名人言论会越来越多。",
            "evidence": ["AI生成红头文件的演示视频", "国外类似案例报道"],
            "emotional_tone": "fearful",
            "possible_interest": "AI安全领域博主，观点相对独立",
        },
        {
            "source": "本地房产自媒体 @高新区楼市观察",
            "text": "抛开文件真假不谈，高新区这两年发展确实快，地铁通了，万达也开了，房价涨是迟早的事。即使市政府不搬，高新区也是全市最有潜力的板块！买到就是赚到！",
            "evidence": ["高新区房价走势图(选择性展示上涨数据)", "地铁开通新闻"],
            "emotional_tone": "supportive",
            "possible_interest": "该账号运营者为本地房产中介公司负责人，直接利益相关",
        },
        {
            "source": "法律博主 @法山叔",
            "text": "伪造国家机关公文罪(《刑法》第280条)最高可判10年。即便使用的是AI工具，刑事责任依然由操作者承担。此外，中介转发伪造文件进行商业炒作，可能构成虚假宣传，购房者有权主张合同无效要求退款。",
            "evidence": ["刑法第280条原文", "相关司法解释", "类似判例"],
            "emotional_tone": "neutral",
            "possible_interest": "法律科普博主，无利益相关",
        },
    ],
    "social_media": {
        "sentiment_stats": {"angry": 0.30, "fearful": 0.35, "neutral": 0.20, "sarcastic": 0.10, "supportive": 0.05},
        "representative_comments": [
            {
                "user": "@高新区已上车",
                "text": "刚在高新区买的房，现在慌得一批。如果真是中介造谣炒作，我是不是可以告他们退房？？在线等，急！",
                "emotion": "fearful",
                "likes": 12500,
            },
            {
                "user": "@AI安全研究员",
                "text": "检测AI生成文本其实有迹可循：1) 对特定词汇的使用频率异常 2) 句式结构过于工整 3) 连贯性过强缺乏人类写作的自然跳跃。建议大家学习一下基本的鉴别方法。",
                "emotion": "neutral",
                "likes": 18900,
            },
            {
                "user": "@键盘侠协会会长",
                "text": "上次说恒大不会倒，上次说核酸检测不会停，上次说房价不会跌...现在又说'市政府不会搬'。我就问一句：你们说的'真相'有几个是真的？[吃瓜]",
                "emotion": "sarcastic",
                "likes": 23400,
            },
            {
                "user": "@地产打工人",
                "text": "作为从业者说句实话：朋友圈那些'再不买就涨了'的消息，十个有九个是编的。这次用AI伪造红头文件算是'技术升级'了，以前都是自己P个聊天记录就敢发。",
                "emotion": "neutral",
                "likes": 31200,
            },
            {
                "user": "@科技向善",
                "text": "AI生成虚假信息的危害不亚于假币。建议国家尽快出台AI生成内容的强制标注法规，让每个AI生成的图片、文本都带上隐形水印。",
                "emotion": "supportive",
                "likes": 27600,
            },
        ],
    },
}

# ============================================================
# Lookup API
# ============================================================

ALL_SCENARIOS = {
    "ev_crash": SCENARIO_EV_CRASH,
    "donation": SCENARIO_DONATION,
    "ai_fake": SCENARIO_AI_FAKE,
}

SCENARIO_LIST = [
    {"id": "ev_crash", "title": "某品牌新能源车高速碰撞起火，车门锁死致1死2伤", "category": "交通事故 / 产品安全"},
    {"id": "donation", "title": "女子筹款50万救女被曝有3套房：诈捐还是信息滞后？", "category": "社会民生 / 网络众筹"},
    {"id": "ai_fake", "title": "AI伪造红头文件引发购房恐慌：技术滥用的新危机", "category": "科技安全 / 房地产"},
]


def get_mock_news(topic_id: str) -> Optional[dict]:
    """Return mock news data for a given topic ID, or None if not found."""
    return ALL_SCENARIOS.get(topic_id)


def search_mock_news(keyword: str) -> Optional[dict]:
    """Fuzzy match keyword against available scenarios. Returns the best match or None."""
    keyword_lower = keyword.lower()
    for sid, scenario in ALL_SCENARIOS.items():
        if keyword_lower in scenario["topic"].lower():
            return scenario
    # Return first scenario as default if no match
    return None


def list_scenarios() -> list[dict]:
    """Return all available mock scenarios for display."""
    return SCENARIO_LIST


# Allow running as script to print all mock data
if __name__ == "__main__":
    import json

    for sid, scenario in ALL_SCENARIOS.items():
        print(f"\n{'='*60}")
        print(f"Scenario: {sid}")
        print(f"Topic: {scenario['topic']}")
        print(f"{'='*60}")
        # Print summary only, not full data
        print(f"  5W1H: {scenario['summary_5w1h']['what'][:80]}...")
        print(f"  Official sources: {len(scenario['official']['statements'])} statements")
        print(f"  We-media sources: {len(scenario['we_media'])} articles")
        print(f"  Social sentiment: {scenario['social_media']['sentiment_stats']}")
        print(f"  Comments: {len(scenario['social_media']['representative_comments'])} representative")
