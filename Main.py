from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, CallbackContext, Application, MessageHandler, filters
import random
from youtubesearchpython import VideosSearch
from bs4 import BeautifulSoup
import requests
from googlesearch import search
import os
import datetime
import re
import cmath


TOKEN = '6820034900:AAGyDukDNTizdNPMBdxhNCKinJd0avQxask'
BOT_USERNAME = 'AxvoraBot'
AUTHOR = 'Nelshen Yong'

# Add a state for conversation
START_MENU = 0

async def start_command(update: Update, context):
    # Create an inline keyboard with multiple buttons
    keyboard = [
        [
            InlineKeyboardButton("Menu", callback_data='button_menu'),
            InlineKeyboardButton("Study", callback_data='button_study')
        ],
        [
            InlineKeyboardButton("About", callback_data='button_about'),
            InlineKeyboardButton("Contact", callback_data='button_contact')
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(f'Halo! Terima kasih telah berbicara dengan saya! Saya adalah {BOT_USERNAME}!', reply_markup=reply_markup)

# Feedback
FEEDBACK_FILE_PATH = 'feedback.txt'
async def feedback_command(update: Update, context):
    user_id = update.message.from_user.id
    feedback_text = ' '.join(context.args).strip()

    if not feedback_text:
        await update.message.reply_text('Mohon sertakan teks feedback Anda.')
        return

    save_feedback_to_file(user_id, feedback_text)

    await update.message.reply_text('Terima kasih atas masukan Anda! Saran Anda telah dicatat.')

def save_feedback_to_file(user_id, feedback_text):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    formatted_feedback = f'{timestamp} - User ID {user_id}: {feedback_text}\n'

    # Memastikan file feedback ada
    if not os.path.exists(FEEDBACK_FILE_PATH):
        with open(FEEDBACK_FILE_PATH, 'w') as file:
            file.write('Feedback Log:\n')

    # Menambahkan feedback baru ke file
    with open(FEEDBACK_FILE_PATH, 'a') as file:
        file.write(formatted_feedback)

async def menu_command(update: Update, context):
    await update.message.reply_text(f'Menu {BOT_USERNAME} - List Commands\n\n/study - Menampilkan fitur untuk belajar.\n/about - Menampilkan informasi dari {BOT_USERNAME}.\n/search - Mencari sumber dalam internet.\n/youtube - Mencari video dari Youtube.\n/contact - Mempilkan kontak dari {BOT_USERNAME}.\n/feedback - Memberikan saran kepada {BOT_USERNAME}\n/dice - Menghasilkan angka dadu secara acak.')
    
async def study_command(update: Update, context):
    await update.message.reply_text(f'Menu AxvoraBot - Study Commands\n\n/calculator - Menghitung dari perhitungan sederhana.\n/geometry - Menghitung dari perhitungan geometri sederhana\n/physics - Menghitung dari perhitungan fisika sederhana\n/economics - Menghitung dari perhitungan ekonomi sederhana\n/study_help - Bantuan untuk perintah dalam Study Commands\n')

async def study_help_command(update: Update, context):
    await update.message.reply_text(f'Study Bot Help')
    
async def about_command(update: Update, context):
    await update.message.reply_text(f'{BOT_USERNAME} adalah sebuah bot Telegram yang dikembangkan oleh {AUTHOR}. {BOT_USERNAME} adalah asisten virtual yang dirancang untuk memberikan bantuan dalam belajar berbagai mata pelajaran, termasuk matematika, fisika, dan ekonomi. Bot ini menyediakan fungsi kalkulator untuk menghitung berbagai rumus matematika, fisika, dan ekonomi, dan fitur tambahan lainnya sehingga membantu pengguna dalam mengeksplorasi pembelajaran yang menyenangkan.')

async def contact_command(update: Update, context):
    await update.message.reply_text('Contact us:\nYou can reach us at contact@axvora.com')

async def roll_dice_command(update: Update, context):
    dice_result = random.randint(1, 6)
    emoji_dice = '🎲'
    await update.message.reply_text(f'{emoji_dice} You rolled a {dice_result}! {emoji_dice}')

async def youtube_search_command(update: Update, context):
    if context.args:
        query = ' '.join(context.args)

        # Default number of results is set to 3, change as needed
        num_results = 5

        try:
            # If the user provides a number, use it as the number of results
            if context.args[-1].isdigit():
                num_results = int(context.args[-1])
                query = ' '.join(context.args[:-1])

            video_search = VideosSearch(query, limit=num_results)
            results = video_search.result()

            if results and 'result' in results and results['result']:
                response_text = f'Here are the top {num_results} results for "{query}" on YouTube:\n'
                for i, result in enumerate(results['result'], start=1):
                    video_title = result['title']
                    video_url = result['link']
                    response_text += f'{i}. {video_title}\n{video_url}\n\n'

                await update.message.reply_text(response_text)
            else:
                await update.message.reply_text(f'Sorry, no results found for "{query}" on YouTube.')
        except ValueError:
            await update.message.reply_text('Please provide a valid number for the search results.')
    else:
        await update.message.reply_text('Please provide a search query for YouTube.')


async def google_search_command(update: Update, context: CallbackContext):
    if context.args:
        query = ' '.join(context.args)

        # Default number of results is set to 3, change as needed
        num_results = 5

        try:
            # If the user provides a number, use it as the number of results
            if context.args[-1].isdigit():
                num_results = int(context.args[-1])
                query = ' '.join(context.args[:-1])

            search_results = search(query, num_results=num_results)
            results_list = list(search_results)

            if results_list:
                response_text = f'Here are the top {num_results} results for "{query}":\n'
                for i, result in enumerate(results_list, start=1):
                    title = get_title_from_link(result)
                    response_text += f'{i}. {title}\n{result}\n\n'

                await update.message.reply_text(response_text)
            else:
                await update.message.reply_text(f'Sorry, no results found for "{query}" on Google.')
        except ValueError:
            await update.message.reply_text('Please provide a valid number for the search results.')
    else:
        await update.message.reply_text('Please provide a search query for Google.')

def get_title_from_link(link):
    try:
        response = requests.get(link)
        soup = BeautifulSoup(response.text, 'html.parser')
        title_tag = soup.find('title')
        return title_tag.text if title_tag else 'Untitled'
    except Exception as e:
        print(f'Error fetching title from link: {str(e)}')
        return 'Untitled'
    
async def physics_command(update: Update, context: CallbackContext):
    user_input = ' '.join(context.args).lower()

    formulas = ['force', 'kinetic_energy', 'velocity', 'acceleration', 'work', 'power', 'potential_energy']

    if any(formula in user_input for formula in formulas):
        try:
            if 'force' in user_input:
                result = calculate_force(user_input)
            elif 'kinetic_energy' in user_input:
                result = calculate_kinetic_energy(user_input)
            elif 'velocity' in user_input:
                result = calculate_velocity(user_input)
            elif 'acceleration' in user_input:
                result = calculate_acceleration(user_input)
            elif 'work' in user_input:
                result = calculate_work(user_input)
            elif 'power' in user_input:
                result = calculate_power(user_input)
            elif 'potential_energy' in user_input:
                result = calculate_potential_energy(user_input)
            else:
                result = 'Invalid formula specified. Please choose from force, kinetic_energy, velocity, or acceleration.'

            await update.message.reply_text(result)
        except Exception as e:
            await update.message.reply_text(f'Error in calculation: {str(e)}')
    else:
        await update.message.reply_text('Invalid formula specified. Please choose from force, kinetic_energy, velocity, or acceleration.')

def calculate_force(user_input):
    mass = get_numeric_value(user_input, 'mass')
    acceleration = get_numeric_value(user_input, 'acceleration')
    force = mass * acceleration
    return f'Force - Result: {force} N'

def calculate_kinetic_energy(user_input):
    mass = get_numeric_value(user_input, 'mass')
    velocity = get_numeric_value(user_input, 'velocity')
    kinetic_energy = 0.5 * mass * velocity**2
    return f'Kinetic Energy - Result: {kinetic_energy} J'

def calculate_velocity(user_input):
    initial_velocity = get_numeric_value(user_input, 'initial_velocity')
    acceleration = get_numeric_value(user_input, 'acceleration')
    time = get_numeric_value(user_input, 'time')
    velocity = initial_velocity + acceleration * time
    return f'Velocity - Result: {velocity} m/s'

def calculate_acceleration(user_input):
    change_in_velocity = get_numeric_value(user_input, 'change_in_velocity')
    time = get_numeric_value(user_input, 'time')
    acceleration = change_in_velocity / time
    return f'Acceleration - Result: {acceleration} m/s^2'

def calculate_work(user_input):
    force = get_numeric_value(user_input, 'force')
    displacement = get_numeric_value(user_input, 'displacement')
    work = force * displacement
    return f'Work - Result: {work} J'

def calculate_power(user_input):
    work_done = get_numeric_value(user_input, 'work_done')
    time = get_numeric_value(user_input, 'time')
    power = work_done / time
    return f'Power - Result: {power} W'

def calculate_potential_energy(user_input):
    mass = get_numeric_value(user_input, 'mass')
    height = get_numeric_value(user_input, 'height')
    potential_energy = mass * 9.8 * height
    return f'Gravitational Potential Energy - Result: {potential_energy} J'

async def economics_command(update: Update, context: CallbackContext):
    user_input = ' '.join(context.args).lower()

    try:
        if 'simple_interest' in user_input:
            result = calculate_simple_interest(user_input)
        elif 'compound_interest' in user_input:
            result = calculate_compound_interest(user_input)
        elif 'profit_percentage' in user_input:
            result = calculate_profit_percentage(user_input)
        elif 'profit_loss' in user_input:
            result = calculate_profit_loss(user_input)
        else:
            raise ValueError('Invalid economic calculation. Please choose from simple_interest, compound_interest, profit_percentage, or profit_loss.')

        await update.message.reply_text(result)
    except Exception as e:
        await update.message.reply_text(f'Error in calculation: {str(e)}')

def calculate_simple_interest(user_input):
    principal = get_numeric_value(user_input, 'principal')
    rate = get_numeric_value(user_input, 'rate')
    time = get_numeric_value(user_input, 'time')
    simple_interest = (principal * rate * time) / 100
    return f'Simple Interest - Result: {simple_interest}'

def calculate_compound_interest(user_input):
    principal = get_numeric_value(user_input, 'principal')
    rate = get_numeric_value(user_input, 'rate')
    time = get_numeric_value(user_input, 'time')
    compound_interest = principal * (1 + rate / 100)**time - principal
    return f'Compound Interest - Result: {compound_interest}'

def calculate_profit_percentage(user_input):
    cost_price = get_numeric_value(user_input, 'cost_price')
    selling_price = get_numeric_value(user_input, 'selling_price')
    profit_percentage = ((selling_price - cost_price) / cost_price) * 100
    return f'Profit Percentage - Result: {profit_percentage}%'

def calculate_profit_loss(user_input):
    cost_price = get_numeric_value(user_input, 'cost_price')
    selling_price = get_numeric_value(user_input, 'selling_price')
    profit_loss = selling_price - cost_price

    if profit_loss > 0:
        return f'Profit - Result: {profit_loss}'
    elif profit_loss < 0:
        return f'Loss - Result: {abs(profit_loss)}'
    else:
        return 'No Profit, No Loss'


# Add a new async function to handle button clicks
async def button_click(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data
    
    print(f'Button clicked! Callback data: {data}')

    if data == 'button_menu':
        await query.message.reply_text(f'Menu {BOT_USERNAME} - List Commands\n\n/study - Menampilkan fitur untuk belajar.\n/about - Menampilkan informasi dari {BOT_USERNAME}.\n/search - Mencari sumber dalam internet.\n/youtube - Mencari video dari Youtube.\n/contact - Mempilkan kontak dari {BOT_USERNAME}.\n/feedback - Memberikan saran kepada {BOT_USERNAME}\n/dice - Menghasilkan angka dadu secara acak.')
    elif data == 'button_about':
        await query.message.reply_text(f'{BOT_USERNAME} adalah sebuah bot Telegram yang dikembangkan oleh {AUTHOR}. {BOT_USERNAME} adalah asisten virtual yang dirancang untuk memberikan bantuan dalam belajar berbagai mata pelajaran, termasuk matematika, fisika, dan ekonomi. Bot ini menyediakan fungsi kalkulator untuk menghitung berbagai rumus matematika, fisika, dan ekonomi, dan fitur tambahan lainnya sehingga membantu pengguna dalam mengeksplorasi pembelajaran yang menyenangkan.')
    elif data == 'button_study':
        await query.message.reply_text(f'Button study')
    elif data == 'button_contact':
        await query.message.reply_text('Button 4 is clicked!')
    else:
        await query.message.reply_text(f'Unknown button clicked: {data}')

    # IMPORTANT: Acknowledge the button click
    await context.bot.send_chat_action(chat_id=query.message.chat_id, action="typing")
    
async def calculate_command(update: Update, context: CallbackContext):
    user_input = ' '.join(context.args)

    # Remove non-numeric and non-operator characters
    cleaned_input = re.sub(r'[^0-9+\-*/().]', '', user_input)

    try:
        result = eval(cleaned_input)
        await update.message.reply_text(f'Result: {result}')
    except Exception as e:
        await update.message.reply_text(f'Error in calculation: {str(e)}')
        
async def geometry_command(update: Update, context: CallbackContext):
    user_input = ' '.join(context.args).lower()

    shapes = ['square', 'rectangle', 'circle', 'triangle']

    if any(shape in user_input for shape in shapes):
        try:
            if 'square' in user_input:
                result = calculate_square(user_input)
            elif 'rectangle' in user_input:
                result = calculate_rectangle(user_input)
            elif 'circle' in user_input:
                result = calculate_circle(user_input)
            elif 'triangle' in user_input:
                result = calculate_triangle(user_input)
            else:
                result = 'Invalid shape specified. Please choose from square, rectangle, circle, or triangle.'

            await update.message.reply_text(result)
        except Exception as e:
            await update.message.reply_text(f'Error in calculation: {str(e)}')
    else:
        await update.message.reply_text('Invalid shape specified. Please choose from square, rectangle, circle, or triangle.')

def calculate_square(user_input):
    side_length = get_numeric_value(user_input, 'side')
    area = side_length ** 2
    perimeter = 4 * side_length
    return f'Square - Area: {area} | Perimeter: {perimeter}'

def calculate_rectangle(user_input):
    sides = get_numeric_values(user_input, ['length', 'width'])
    area = sides[0] * sides[1]
    perimeter = 2 * (sides[0] + sides[1])
    return f'Rectangle - Area: {area} | Perimeter: {perimeter}'

def calculate_circle(user_input):
    radius = get_numeric_value(user_input, 'radius')
    area = cmath.pi * (radius ** 2)
    circumference = 2 * cmath.pi * radius
    return f'Circle - Area: {area} | Circumference: {circumference}'

def calculate_triangle(user_input):
    sides = get_numeric_values(user_input, ['side1', 'side2', 'side3'])
    s = sum(sides) / 2
    area = cmath.sqrt(s * (s - sides[0]) * (s - sides[1]) * (s - sides[2]))
    perimeter = sum(sides)
    return f'Triangle - Area: {area} | Perimeter: {perimeter}'

def get_numeric_value(user_input, parameter):
    match = re.search(rf'{parameter}\s*=\s*(-?\d+\.?\d*)', user_input)
    if match:
        return float(match.group(1))
    else:
        raise ValueError(f'Missing or invalid {parameter} value.')

def get_numeric_values(user_input, parameters):
    values = []
    for parameter in parameters:
        values.append(get_numeric_value(user_input, parameter))
    return values

# Responses
def handle_response(text: str):
    processed: str = text.lower()
    
    if 'p' in processed:
        return 'p!'
    
    if 'halo' in processed:
        return 'Halo!'
    
    if 'hello' in processed:
        return 'Hey there!'
    
    if 'hi' in processed:
        return 'Hi! How can I help you?'
    
    if 'how are you' in processed:
        return 'I am good!'
    
    if 'what\'s up' in processed or 'sup' in processed:
        return 'Not much, just chatting. How about you?'
    
    if 'i love python' in processed:
        return 'I love Python too!'
    
    if 'tell me a joke' in processed:
        return 'Why did the Python programmer get bitten by a snake? Because he used "Python 2"!'
    
    if 'favorite programming language' in processed:
        return 'I might be biased, but I really like Python. What about you?'
    
    if 'where are you from' in processed:
        return 'I am a virtual assistant, so I don\'t have a specific location. But I\'m here to assist you!'
    
    if 'thank you' in processed or 'thanks' in processed:
        return 'You\'re welcome! If you have more questions, feel free to ask.'
    
    return 'I do not understand what you wrote...'

async def handle_message(update: Update, context):
    message_type: str = update.message.chat.type
    text: str = update.message.text
    
    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')
    
    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = handle_response(new_text)
        else:
            return
    else:
        response: str = handle_response(text)
        
    print('Bot:', response)
    await update.message.reply_text(response)

async def error(update: Update, context):
    print(f'Update {update} caused error {context.error}')

if __name__ == '__main__':
    print('Bot is starting...')
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('menu', menu_command))
    app.add_handler(CommandHandler('study_help', study_help_command))
    app.add_handler(CommandHandler('study', study_command))
    app.add_handler(CommandHandler('about', about_command))
    app.add_handler(CommandHandler('contact', contact_command))
    app.add_handler(CommandHandler('dice', roll_dice_command))
    app.add_handler(CommandHandler('youtube', youtube_search_command))
    app.add_handler(CommandHandler('search', google_search_command))
    app.add_handler(CommandHandler('feedback', feedback_command))
    app.add_handler(CommandHandler('calculate', calculate_command))
    app.add_handler(CommandHandler('geometry', geometry_command))
    app.add_handler(CommandHandler('physics', physics_command))
    app.add_handler(CommandHandler('economics', economics_command))


    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Callback Query
    app.add_handler(CallbackQueryHandler(button_click))

    # Error
    app.add_error_handler(error)

    # Polls the bot
    print('Polling...')
    app.run_polling(poll_interval=3)
