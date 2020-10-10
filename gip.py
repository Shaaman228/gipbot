# imports
import discord
from discord.ext import commands

from discord.utils import get
import youtube_dl
import os

import shutil

import config

# key symbol
client = commands.Bot( command_prefix = config.PREFIX )
client.remove_command( 'help' )

# bot joined to server
@client.event
async def on_ready():
	print( '[log] ' + client.user.name + ' connected\n' )

	await client.change_presence( status = discord.Status.online, activity = discord.Game( 'ящик ⚰️' ) )

# .cls N
@client.command()
# can use
@commands.has_permissions( administrator = True )
async def cls( ctx, amount : int ):

	# get author
	author = ctx.message.author.name

	# delete command
	await ctx.channel.purge( limit = amount + 1 )

	# comment
	if amount == 1:
		title_emb = f'🍻  { author } очистил ' + str(amount) + ' строку. Вопрос - нахуя?'
	elif amount > 1 and amount < 5:
		title_emb = f'🍻  { author } очистил ' + str(amount) + ' строки.'
	else:
		title_emb = f'🍻  { author } очистил ' + str(amount) + ' строк.'

	emb=discord.Embed( title = title_emb, colour = 0x708649)
	await ctx.send( embed = emb )

# .join
@client.command( pass_context = True, aliases = ['j'] )
async def join( ctx ):
	global voice
	channel = ctx.message.author.voice.channel
	voice = get( client.voice_clients, guild = ctx.guild )

	if voice and voice.is_connected():
		await voice.move_to( channel )
	else:
		voice = await channel.connect()
		print( f'[log] The bot has connected to { channel }\n' )

	await ctx.send( f'Зашёл в { channel }' )

# .leave
@client.command( pass_context = True, aliases = ['l', 'out'] )
async def leave( ctx ):
	channel = ctx.message.author.voice.channel
	voice = get( client.voice_clients, guild = ctx.guild )
	author = ctx.message.author.name

	if voice and voice.is_connected():
		await voice.disconnect()
		print( f'[log] The bot has left { channel }' )
		await ctx.send( f'Вышел из { channel }' )
	else:
		print( '[log] Bot was told to leave voice channel, but was not in one' )
		await ctx.send( f'Не помню, что бы я куда-то подлючался { author }  😡' )

ncname = ' '

# .play
@client.command( pass_context = True, aliases = [ 'p' ] )
async def play( ctx, url : str ):

	def check_queue():

		Plist_infile = os.path.isdir( './playlist' )

		if Plist_infile is True:
			DIR = os.path.abspath( os.path.realpath( 'playlist' ) )
			length = len( os.listdir(DIR) )
			still_p = length - 1

			try:
				first_file = os.listdir(DIR)[ 0 ]
			except:
				print( '[log] no more queued song(s)\n' )
				plist.clear()
				return

			main_location = os.path.dirname( os.path.realpath(__file__) )
			song_path = os.path.abspath( os.path.realpath( 'playlist' ) + '\\' + first_file )

			if length != 0:
				print( '[log] song done, playing next\n' )
				print( f'[log] songs still in playlist: { still_p }' )
				song_there = os.path.isfile( 'song.mp3' )
				if song_there:
					os.remove( 'song.mp3' )
				shutil.move( song_path, main_location )
				for file in os.listdir( './' ):
					if file.endswith( '.mp3' ):
						name = file
						print( f'[log] Renamed file: {file} to song.mp3\n' )
						os.rename( file, 'song.mp3' )

				voice.play( discord.FFmpegPCMAudio( 'song.mp3' ), after = lambda e: check_queue() )
				voice.source = discord.PCMVolumeTransformer( voice.source )
				voice.source.voice = 0.07

				nname = name.rsplit( '-', 2 )

				ncname = 'Играет - '
				i = 0
				while i < int( len( nname ) - 1 ):
					ncname = ncname + nname[ i ]
					i = i + 1

				print ( '[log] ' + ncname     + '\n' )

				emb = discord.Embed( title = ncname, description = f'Заказал - { author }', colour = 0x708649, url = url)

			else: 
				plist.claer()
				return

		else:
			plist.clear()
			print( '[log] no songs were queued before the ending of the last song\n' )

	author = ctx.message.author.name
	song_there = os.path.isfile( 'song.mp3' )

	try:
		if song_there:
			os.remove( 'song.mp3' )
			plist.clear()
			print( '[log] Removed old song file' )
	except PermissionError:
		print( '[log] song аdding to queue' )
		await add( ctx, url )
		return

	Plist_infile = os.path.isdir( './playlist' )

	try:
		Plist_folder = './playlist'

		if Plist_infile is True:
			print( '[log] removed old playlist folder' )
			shutil.rmtree( Plist_folder )

	except:
		print( '[log] no old queue folder' )

	await ctx.send( 'Итак, всё готово' )

	voice = get( client.voice_clients, guild = ctx.guild )

	ydl_opts = {
		'format' : 'bestaudio/best',
		'postprocessors' : [{ 
			'key' : 'FFmpegExtractAudio',
			'preferredcodec' : 'mp3',
			'preferredquality' : '192',
		}],
	}

	with youtube_dl.YoutubeDL(ydl_opts) as ydl:
		print( '[log] Downloading audio now\n' )
		ydl.download( [ url ] )

	for file in os.listdir( './' ):
		if file.endswith( '.mp3' ):
			name = file
			print( f'[log] Renamed file: {file} to song.mp3\n' )
			os.rename( file, 'song.mp3' )

	nname = name.rsplit( '-', 2 )

	ncname = 'Играет - '
	i = 0
	while i < int( len( nname ) - 1 ):
		ncname = ncname + nname[ i ]
		i = i + 1

	print ( '[log] ' + ncname     + '\n' )

	emb = discord.Embed( title = ncname, description = f'Заказал - { author }', colour = 0x708649, url = url)
	await ctx.send( embed = emb )

	voice.play( discord.FFmpegPCMAudio( 'song.mp3' ), after = lambda e: check_queue() )
	voice.source = discord.PCMVolumeTransformer( voice.source )
	voice.source.voice = 0.07

# .pop
@client.command()
async def pop( ctx ):
	voice = get( client.voice_clients, guild = ctx.guild )

	if voice and voice.is_playing():
		voice.pause()
		print( '[log] Music paused\n' )
		await ctx. send( 'Музыка на паузе' )
	else:
		voice.resume()
		print( '[log] Resumed music\n' )
		await ctx. send( 'Музыка играет' )

# .skip
@client.command( pass_context = True, aliases = [ 's' ] )
async def skip( ctx ):
	voice = get( client.voice_clients, guild = ctx.guild )

	if voice and voice.is_playing():
		voice.stop()
		print( '[log] Music stopped\n' )
		await ctx. send( 'Музыка остановлена' )
	else:
		print( '[log] Failed music stopped - music not playing\n' )
		await ctx. send( 'Музыка не играла' )

# .stop
@client.command()
async def stop( ctx ):
	voice = get( client.voice_clients, guild = ctx.guild )

	plist.clear()

	if voice and voice.is_playing():
		voice.stop()
		print( '[log] Music stopped\n' )
		await ctx. send( 'Музыка остановлена' )
	else:
		print( '[log] Failed music stopped - music not playing\n' )
		await ctx. send( 'Музыка не играла' )

plist = {}

# .add
#@client.command( pass_context = True, aliases = [ 'a' ] )
async def add( ctx, url : str ):
	Plist_infile = os.path.isdir( './playlist' )

	if Plist_infile is False:
		os.mkdir( 'playlist' )

	DIR = os.path.abspath( os.path.realpath( 'playlist' ) )
	p_num = len( os.listdir( DIR ) )
	p_num += 1
	add_plist = True
	while add_plist:
		if p_num in plist:
			p_num += 1
		else:
			add_plist = False
			plist[ p_num ] = p_num

	plist_path = os.path.abspath( os.path.realpath( 'playlist' ) + f'\song{p_num}.%(ext)s' )

	ydl_opts = {
		'format' : 'bestaudio/best',
		'outtmpl' : plist_path,
		'postprocessors' : [{ 
			'key' : 'FFmpegExtractAudio',
			'preferredcodec' : 'mp3',
			'preferredquality' : '192',
		}],
	}

	with youtube_dl.YoutubeDL(ydl_opts) as ydl:
		print( '[log] Downloading audio now\n' )
		ydl.download( [ url ] )

	await ctx.send( 'Добавлено ' + str( p_num ) + ' в очередь' )
	print( '[log] song added to plist\n' )

# .help
@client.command()
async def help( ctx ):

	# command list
	emb = discord.Embed( title = '[===== Команды на сервере =====]', color = 0x708649 )

	emb.add_field( name   = '🧹  {}cls'.format( config.PREFIX ), 
		           value  = 'очистка чата', 
		           inline = False)

	emb.add_field( name   = '🔔  {}join/j'.format( config.PREFIX ), 
		           value  = 'призвать бота' , 
		           inline = False)

	emb.add_field( name   = '🔇  {}leave/l/out'.format( config.PREFIX ), 
		           value  = 'отзвать бота' , 
		           inline = False)

	emb.add_field( name   = '📻  {}play/p'.format( config.PREFIX ), 
		           value  = 'проигрыванье песен-ок' , 
		           inline = False)

	emb.add_field( name   = '⏯️  {}pop'.format( config.PREFIX ), 
		           value  = 'остановка или продолжение трека' , 
		           inline = False)

	emb.add_field( name   = '⏭️  {}skip/s'.format( config.PREFIX ), 
		           value  = 'Пропуск песни' , 
		           inline = False)

	emb.add_field( name   = '⏹️  {}stop'.format( config.PREFIX ), 
		           value  = 'Пропуск плейлиста' , 
		           inline = False)

	emb.add_field( name   = 'ℹ️  {}help'.format( config.PREFIX ),  
		           value  = 'вызывает эту функцию', 
		           inline = False)

	#send list
	await ctx.send( embed = emb )

# Errors
@client.command()

async def on_command_error( ctx, error ):
	pass

# cls errors
@cls.error

async def cls_error( ctx, error ):

	print( isinstance )

	if isinstance( error, commands.MissingRequiredArgument ):
		await ctx.send( f'{ ctx.author.mention }, я тебе чё гадалка? Сколько удалять напиши' )

	if isinstance( error, commands.MissingPermissions ):
		await ctx.send( f'{ ctx.author.mention }, у тебя нет прав' )

	if isinstance( error, commands.CommandNotFound ):
		await ctx.send( f'{ ctx.author.mention }, нет такой команды!' )

# Connect
token = config.TOKEN
client.run( str(token) )
