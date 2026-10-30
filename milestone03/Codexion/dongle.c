/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   dongle.c                                           :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: kyonaha <kyonaha@student.42tokyo.jp>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/10/06 12:23:31 by kyonaha           #+#    #+#             */
/*   Updated: 2026/10/06 12:40:00 by kyonaha          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "codexion.h"

static long	next_wakeup(t_coder *c)
{
	long	now;
	long	until;
	long	at;

	now = now_us();
	until = now + WAIT_CAP_US;
	at = dongle_available_at(c->first);
	if (at > now && at < until)
		until = at;
	at = dongle_available_at(c->second);
	if (at > now && at < until)
		until = at;
	return (until);
}

static void	wait_turn(t_coder *c)
{
	struct timespec	ts;
	long			until;
	long			left;

	until = next_wakeup(c);
	left = until - now_us();
	if (left <= 0)
		return ;
	if (left <= PRECISE_WINDOW_US)
	{
		pthread_mutex_unlock(&c->table->arbiter);
		usleep(left / 2 + 1);
		pthread_mutex_lock(&c->table->arbiter);
		return ;
	}
	until -= PRECISE_WINDOW_US;
	ts.tv_sec = until / 1000000;
	ts.tv_nsec = (until % 1000000) * 1000;
	pthread_cond_timedwait(&c->wake, &c->table->arbiter, &ts);
}

int	take_dongles(t_coder *c)
{
	t_table	*t;
	int		taken;

	t = c->table;
	pthread_mutex_lock(&t->arbiter);
	request_dongles(c);
	taken = try_take(c);
	while (!taken && !is_stopped(t))
	{
		wait_turn(c);
		taken = try_take(c);
	}
	pthread_mutex_unlock(&t->arbiter);
	return (taken);
}

void	release_dongles(t_coder *c)
{
	t_table	*t;
	long	available_at;
	int		n;

	t = c->table;
	n = t->args.number_of_coders;
	available_at = now_us() + t->args.dongle_cooldown * 1000L;
	pthread_mutex_lock(&t->arbiter);
	dongle_release(c->first, available_at);
	dongle_release(c->second, available_at);
	pthread_cond_signal(&t->coders[(c->id - 2 + n) % n].wake);
	pthread_cond_signal(&t->coders[c->id % n].wake);
	pthread_mutex_unlock(&t->arbiter);
}
