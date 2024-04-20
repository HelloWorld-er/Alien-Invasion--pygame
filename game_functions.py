import pygame
import sys
from time import sleep
import json

from bullet import Bullet
from alien import Alien
import preprocessing


def update_high_score_history_data(stats):
	with open("../All-in-One/Alien Invasion/users_data.json", "r+") as users_data_file:
		users_data_list = json.load(users_data_file)
		for user_data in users_data_list:
			if user_data[0] == stats.user:
				user_data[1]['high score'] = stats.high_score
				users_data_file.seek(0, 0)
				json.dump(users_data_list, users_data_file)
				break
	with open("../All-in-One/Alien Invasion/high_score_data.json", "w") as high_score_data_file:
		json.dump({"user": stats.user, "high score": stats.high_score_history}, high_score_data_file)


def check_keydown_events(event, ai_settings, screen, stats, username_input_text, ship, bullets):
	if event.key == pygame.K_q:
		update_high_score_history_data(stats)
		sys.exit()
	elif stats.input_username:
		if event.key == pygame.K_RIGHT:
			ship.moving_right = True
		elif event.key == pygame.K_LEFT:
			ship.moving_left = True
		elif event.key == pygame.K_SPACE:
			fire_bullet(ai_settings, screen, ship, bullets)
	elif stats.username_start_input:
		username_input_text.writing = True
		if event.key == pygame.K_RETURN:
			username_input_text.text += "\n"
		elif event.key == pygame.K_BACKSPACE:
			username_input_text.text = username_input_text.text[:-1]
		else:
			username_input_text.text += event.unicode
		username_input_text.text = username_input_text.text.strip()


def fire_bullet(ai_settings, screen, ship, bullets):
	if len(bullets) < ai_settings.bullets_allowed:
		new_bullet = Bullet(ai_settings, screen, ship)
		bullets.add(new_bullet)


def check_keyup_events(event, ship):
	if event.key == pygame.K_RIGHT:
		ship.moving_right = False
	elif event.key == pygame.K_LEFT:
		ship.moving_left = False


def check_events(ai_settings, screen, stats, introduction_of_game, next_button, back_button, username_input_text, username_confirm, score_board, play_button, ship,
                 aliens, bullets):
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			update_high_score_history_data(stats)
			sys.exit()
		elif event.type == pygame.KEYDOWN:
			check_keydown_events(event, ai_settings, screen, stats, username_input_text, ship, bullets)
		elif event.type == pygame.KEYUP:
			check_keyup_events(event, ship)
		elif event.type == pygame.MOUSEBUTTONDOWN:
			mouse_x, mouse_y = pygame.mouse.get_pos()
			check_button(ai_settings, screen, stats, introduction_of_game, next_button, back_button, username_input_text, username_confirm, score_board, play_button,
			             ship, aliens, bullets, mouse_x, mouse_y)


def check_button(ai_settings, screen, stats, introduction_of_game, next_button, back_button, user_input_text, username_confirm, score_board, play_button, ship, aliens,
                 bullets, mouse_x, mouse_y):
	stats.username_start_input = False
	user_input_text.writing = False
	if stats.view_introduction is True:
		if next_button.rect.collidepoint(mouse_x, mouse_y):
			if stats.introduction_page == stats.introduction_total_pages - 1:
				stats.view_introduction = False
				stats.introduction_page = 0
			else:
				stats.introduction_page += 1
			preprocessing.next_button_prep(next_button, stats, introduction_of_game)
			preprocessing.back_button_prep(back_button, next_button)
		elif back_button.rect.collidepoint(mouse_x, mouse_y):
			if stats.introduction_page > 0:
				stats.introduction_page -= 1
			preprocessing.next_button_prep(next_button, stats, introduction_of_game)
			preprocessing.back_button_prep(back_button, next_button)
	elif play_button.rect.collidepoint(mouse_x, mouse_y) and not stats.game_active and stats.input_username:
		ai_settings.initialize_dynamic_settings()
		pygame.mouse.set_visible(False)
		stats.reset_stats()
		stats.game_active = True
		
		score_board.prep_high_score_history()
		score_board.prep_high_score_history_user()
		score_board.prep_high_score()
		score_board.prep_score()
		score_board.prep_level()
		score_board.prep_user()
		score_board.prep_ships()
		
		aliens.empty()
		bullets.empty()
		
		create_fleet(ai_settings, screen, ship, aliens)
		ship.center_ship()
	elif user_input_text.rect.collidepoint(mouse_x, mouse_y) and not stats.input_username:
		stats.username_start_input = not stats.username_start_input
	elif username_confirm.rect.collidepoint(mouse_x, mouse_y) and not stats.input_username:
		if len(user_input_text.text):
			stats.input_username = True
			stats.user = user_input_text.text
			score_board.prep_user()
			already_registered = False
			with open("../All-in-One/Alien Invasion/users_data.json", "r+") as users_data_file:
				users_data_list = json.load(users_data_file)
				if users_data_list != []:
					for user_data in users_data_list:
						if user_data[0] == stats.user:
							stats.high_score = user_data[1]['high score']
							already_registered = True
							break
				if not already_registered:
					users_data_file.seek(0, 0)
					users_data_list.append([stats.user, {"high score": 0}])
					json.dump(users_data_list, users_data_file)
		else:
			user_input_text.hint = "Username could not be empty!"


def update_screen(ai_settings, screen, stats, introduction_of_game, next_button, back_button, username_input_text, username_confirm, score_board, ship, aliens, bullets,
                  play_button):
	screen.fill(ai_settings.bg_color)
	
	for bullet in bullets.sprites():
		bullet.draw_bullet()
	ship.blitme()
	aliens.draw(screen)
	
	score_board.show_score()
	
	if stats.view_introduction is False:
		if stats.input_username:
			if not stats.game_active:
				play_button.draw_button()
		else:
			username_input_text.draw_input_text()
			username_confirm.draw_button()
	else:
		introduction_of_game[stats.introduction_page].show_label()
		next_button.draw_button()
		back_button.draw_button()
	
	pygame.display.flip()


def update_bullets(ai_settings, screen, stats, score_board, ship, aliens, bullets):
	bullets.update()
	for bullet in bullets.copy():
		if bullet.rect.bottom <= 0:
			bullets.remove(bullet)
	
	check_bullet_alien_collision(ai_settings, screen, stats, score_board, ship, aliens, bullets)


def check_bullet_alien_collision(ai_settings, screen, stats, score_board, ship, aliens, bullets):
	collision = pygame.sprite.groupcollide(bullets, aliens, True, True)
	if collision:
		for alien in collision.values():
			stats.score += ai_settings.alien_points * len(alien)
			score_board.prep_score()
		check_high_score(stats, score_board)
	if len(aliens) == 0:
		bullets.empty()
		ai_settings.increase_speed()
		stats.level += 1
		score_board.prep_level()
		
		create_fleet(ai_settings, screen, ship, aliens)


def get_number_alien_x(ai_settings, alien_width):
	available_space_x = ai_settings.screen_width - 2 * alien_width
	number_aliens_x = int(available_space_x / (2 * alien_width))
	return number_aliens_x


def get_number_rows(ai_settings, ship_height, alien_height):
	available_space_y = ai_settings.screen_height - 3 * alien_height - ship_height
	numbers_rows = int(available_space_y / (2 * alien_height))
	return numbers_rows


def create_alien(ai_settings, screen, aliens, alien_number, row_number):
	alien = Alien(ai_settings, screen)
	alien_width = alien.rect.width
	alien.x = alien_width + 2 * alien_width * alien_number
	alien.rect.x = alien.x
	alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
	aliens.add(alien)


def create_fleet(ai_settings, screen, ship, aliens):
	alien = Alien(ai_settings, screen)
	number_aliens_x = get_number_alien_x(ai_settings, alien.rect.width)
	number_rows = get_number_rows(ai_settings, ship.rect.height, alien.rect.height)
	
	for row_number in range(number_rows):
		for alien_number in range(number_aliens_x):
			create_alien(ai_settings, screen, aliens, alien_number, row_number)


def check_fleet_edges(ai_settings, aliens):
	for alien in aliens.sprites():
		if alien.check_edges():
			change_fleet_direction(ai_settings, aliens)
			break


def change_fleet_direction(ai_settings, aliens):
	for alien in aliens.sprites():
		alien.rect.y += ai_settings.fleet_drop_speed
	ai_settings.fleet_direction *= -1


def ship_hit(ai_settings, stats, screen, score_board, ship, aliens, bullets):
	if stats.ships_left > 0:
		stats.ships_left -= 1
		
		score_board.prep_ships()
		
		aliens.empty()
		bullets.empty()
		
		create_fleet(ai_settings, screen, ship, aliens)
		
		ship.center_ship()
		
		sleep(0.5)
	else:
		stats.game_active = False
		pygame.mouse.set_visible(True)


def check_aliens_bottom(ai_settings, stats, screen, score_board, ship, aliens, bullets):
	screen_rect = screen.get_rect()
	for alien in aliens.sprites():
		if alien.rect.bottom >= screen_rect.bottom:
			ship_hit(ai_settings, stats, screen, score_board, ship, aliens, bullets)
			break


def update_aliens(ai_settings, stats, screen, score_board, ship, aliens, bullets):
	check_fleet_edges(ai_settings, aliens)
	aliens.update()
	
	if pygame.sprite.spritecollideany(ship, aliens):
		ship_hit(ai_settings, stats, screen, score_board, ship, aliens, bullets)
	check_aliens_bottom(ai_settings, stats, screen, score_board, ship, aliens, bullets)


def check_high_score(stats, score_board):
	if stats.score > stats.high_score:
		stats.high_score = stats.score
		score_board.prep_high_score()
	if stats.high_score > stats.high_score_history:
		stats.high_score_history = stats.high_score
		stats.high_score_history_user = stats.user
		score_board.prep_high_score_history()
		score_board.prep_high_score_history_user()
