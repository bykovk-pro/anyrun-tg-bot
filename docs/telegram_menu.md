# Структура меню бота
Файл api/menu.py содержит реализацию меню бота. Меню реализовано с использованием библиотеки InlineKeyboardMarkup. При образении пользователя к боту, сразу должно отображаться главное меню. При переходе в меню, должно отображаться название меню и кнопки для выбора действия.
Если пользователь выбирает пункт меню, который не предполагает перехода в другое меню, то должно выполняться действие, связанное с этим пунктом меню, отображаться результат выполнения действия и вновь показываться меню, из которого было выполнено действие (результат выполнения действия должен быть выведен в отдельном сообщении).
Если пользователь не выбирает пункты в меню, а отправляет сообщение боту, то должен выполняться парсинг этого сообщения на наличие в нём строки URL. Если URL найден, то должен выполняться анализ этого URL с использованием API ANY.RUN Sandbox. Результат анализа должен быть выведен в отдельном сообщении. Во всех остальных случаях введённое сообщение должно игнорироваться.

## Главное меню
1. Sandbox API
2. Settings
3. Help

## Меню Sandbox API
1. Run URL analysis // Ask for URL and run URL analysis and show result (task UUID) in new message
2. Run file analysis // Ask for file and run file analysis and show result (task UUID) in new message
3. Get report // Ask for task UUID and get report and show result in new message
4. History // Show history of your analysis
5. Show your API limits // Show your current API limits
6. Return to main menu

### Меню History
1. Get history // Show history of your analysis by ten reports per page with navigation buttons
2. Get report by UUID // Ask for task UUID and get report and show result in new message
3. Return to Sandbox API menu

## Меню Settings
1. Manage your API key // Show your API keys and manage them
2. Change bot language // Change bot language
3. Check your access rights // Check if user joined to groups listed in .env variable REQUIRED_GROUP_IDS
4. Wipe your data // Ask for confirmation (submenu with two buttons: "Yes" and "No") and wipe your data from database
5. Admin panel // Show if user is bot admin
6. Return to main menu

### Меню Manage your API key
1. Show your API keys // Show your API keys by ten keys per page with navigation buttons    
2. Add new API key // Ask for API key and add it to your API keys
3. Delete API key // Ask for API key and delete it from your API keys
4. Change API key name // Ask for API key and change its name
5. Set active API key // Ask for API key and set it as active
6. Return to Settings menu

### Меню Change bot language
1. Automatically detect language // Automatically detect language of user
2. Set language
3. Return to Settings menu

#### Меню Set language
1. {list of all available language names from *.json files in lang folder} // Show by ten names per page with navigation buttons
2. Return to Change bot language menu

### Меню Admin panel
1. Check bot groups // Check if bot joined to groups listed in .env variable REQUIRED_GROUP_IDS
2. Manage users
3. Manage bot
5. Return to Settings menu

#### Меню Manage users
1. Show all users
2. Ban user by ID // Ask for telegram ID and ban user by ID
3. Unban user by ID // Ask for telegram ID and unban user by ID
4. Delete user by ID // Ask for telegram ID and delete user by ID
5. Return to Admin panel menu

##### Меню Show all users
1. {list of all users in database} // Show by ten users per page with navigation buttons, output format: <telegram_id> <first_access_date> <last_access_date> <is_admin> <is_banned> <is_deleted>
2. Return to Manage users menu

#### Меню Manage bot
1. Restart bot // Ask for confirmation (submenu with two buttons: "Yes" and "No") and restart bot
2. Change bot log level (current: {current_log_level}) // Ask for log level and change it
3. Show bot logs // Show 50 lines from the end of bot logs
4. Show bot statistics // Show bot statistics: total users, total messages, total requests, total errors, total uptime
5. Show system information // Show system information: OS, Python, CPU, RAM, Disk, Network
6. Backup database // Create backup of database and send it to user
7. Return to Admin panel menu

## Меню Help
1. ANY.RUN Sandbox service // Open ANY.RUN Sandbox service in browser   
2. API documentation // Open API documentation in browser
3. Send feedback or report a bug // Ask for message and send it as email to me@bykovk.pro with subject "ANY.RUN Bot feedback" and with body: <message> <user_telegram_id> <user_telegram_username> <bot_statistics> <system_information>
4. Return to main menu