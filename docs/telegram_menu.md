# Bot menu description
Файл api/menu.py содержит реализацию меню бота. Меню реализовано с использованием библиотеки InlineKeyboardMarkup. При обращении пользователя к боту, сразу должно отображаться главное меню. При переходе в меню, должно отображаться название меню и кнопки для выбора действия.
Если пользователь выбирает пункт меню, который не предполагает перехода в другое меню, то должно выполняться действие, связанное с этим пунктом меню, отображаться результат выполнения действия и вновь показываться меню, из которого было выполнено действие (результат выполнения действия должен быть выведен в отдельном сообщении).
Если пользователь не выбирает пункты в меню, а отправляет сообщение боту, то должен выполняться парсинг этого сообщения на наличие в нём строки URL. Если URL найден, то должен выполняться анализ этого URL с использованием API ANY.RUN Sandbox. Результат отправки задачи на анализ - UUID задачи -- должен быть выведен в отдельном сообщении, после чего должно отобразиться меню History. В случае ошибки при отправке задачи на анализ, должно отобразиться сообщение об ошибке и выполнен переход в главное меню. Во всех остальных случаях введённое сообщение должно игнорироваться.

## Main menu
1. Sandbox API // Open Sandbox API menu
2. Settings // Open Settings menu
3. Help // Open Help menu

## Sandbox API menu
1.1. Run URL analysis // Ask for URL and run URL analysis and show result (task UUID) in new message
1.2. Run file analysis // Ask for file and run file analysis and show result (task UUID) in new message
1.3. Get report // Ask for task UUID and get report and show result in new message // Deprecated, must be deleted!
1.4. History // Open History menu
1.5. Show your API limits // Show your current API limits
1.6. Return to main menu

### History menu
1.4.1. Get history // Show history of your analysis by ten reports per page with navigation buttons
1.4.2. Get report by UUID // Ask for task UUID and get report and show result in new message
1.4.3. Return to Sandbox API menu

## Settings menu
2.1. Manage your API key // Open Manage your API key menu
2.2. Change bot language // Open Change bot language menu
2.3. Check your access rights // Check if user joined to groups listed in .env variable REQUIRED_GROUP_IDS
2.4. Wipe your data // Open Wipe your data menu
2.5. Admin panel // Open Admin panel menu if user is bot admin
2.6. Return to main menu

### Manage your API key menu
2.1.1. Show your API keys // Show your API keys by ten keys per page with navigation buttons    
2.1.2. Add new API key // Ask for API key and add it to your API keys
2.1.3. Delete API key // Ask for API key and delete it from your API keys
2.1.4. Change API key name // Ask for API key and change its name
2.1.5. Set active API key // Ask for API key and set it as active
2.1.6. Return to Settings menu

### Change bot language menu
2.2.1. Automatically detect language // Automatically detect language of user
2.2.2. Set language // Open Set language menu
2.2.3. Return to Settings menu

#### Set language menu
2.2.2.1. {list of all available language names from *.json files in lang folder} // Show by ten names per page with navigation buttons
2.2.2.2. Return to Change bot language menu

### Admin panel menu
2.5.1. Check bot groups // Check if bot joined to groups listed in .env variable REQUIRED_GROUP_IDS
2.5.2. Manage users // Open Manage users menu
2.5.3. Manage bot // Open Manage bot menu
2.5.4. Return to Settings menu

#### Manage users menu
2.5.2.1. Show all users // Open Show all users menu
2.5.2.2. Ban user by ID // Ask for telegram ID and ban user by ID
2.5.2.3. Unban user by ID // Ask for telegram ID and unban user by ID
2.5.2.4. Delete user by ID // Ask for telegram ID and delete user by ID
2.5.2.5. Return to Admin panel menu

##### Show all users menu
2.5.2.1.1. {list of all users in database} // Show by ten users per page with navigation buttons, output format: <telegram_id> <first_access_date> <last_access_date> <is_admin> <is_banned> <is_deleted>
2.5.2.1.2. Return to Manage users menu

#### Manage bot menu
2.5.3.1. Restart bot // Ask for confirmation (submenu with two buttons: "Yes" and "No") and restart bot
2.5.3.2. Change bot log level (current: {current_log_level}) // Ask for log level and change it
2.5.3.3. Show bot logs // Show 50 lines from the end of bot logs
2.5.3.4. Show bot statistics // Show bot statistics: total users, total messages, total requests, total errors, total uptime
2.5.3.5. Show system information // Show system information: Bot version, Host name, Host IP, OS, CPU, RAM, Disk, Network usage
2.5.3.6. Backup database // Create backup of database and send it to user
2.5.3.7. Restore database // Ask for backup file and restore database from it
2.5.3.8. Return to Admin panel menu

## Help menu
3.1. ANY.RUN Sandbox service // Open ANY.RUN Sandbox service in browser   
3.2. API documentation // Open API documentation in browser
3.3. Send feedback or report a bug // Ask for message and send it as email to {author_email from setup.py} with subject "ANY.RUN Bot feedback" and with body: <message> <user_telegram_id> <user_telegram_username> <bot_statistics> <system_information>
3.4. Return to main menu