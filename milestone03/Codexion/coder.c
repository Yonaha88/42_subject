/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   coder.c                                            :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: kyonaha <kyonaha@student.42tokyo.jp>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/10/06 12:23:53 by kyonaha           #+#    #+#             */
/*   Updated: 2026/10/06 12:23:54 by kyonaha          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "codexion.h"

static long	compile_once(t_coder *c)
{
	t_table	*t;
	long	end;

	t = c->table;
	if (!take_dongles(c))
		return (-1);
	end = log_compile(c);
	if (end < 0)
	{
		release_dongles(c);
		wake_all(t);
		return (-1);
	}
	end += t->args.time_to_compile * 1000L;
	sleep_until(t, end);
	release_dongles(c);
	pthread_mutex_lock(&c->state_mutex);
	c->compiles++;
	pthread_mutex_unlock(&c->state_mutex);
	return (end);
}

static int	wait_start(t_coder *c)
{
	t_table	*t;

	t = c->table;
	pthread_mutex_lock(&t->arbiter);
	t->arrived++;
	if (t->arrived == t->args.number_of_coders)
		pthread_cond_signal(&t->ready);
	while (!t->started && !is_stopped(t))
		pthread_cond_wait(&c->wake, &t->arbiter);
	pthread_mutex_unlock(&t->arbiter);
	return (!is_stopped(t));
}

static void	*solo_routine(t_coder *c)
{
	log_state(c, "has taken a dongle");
	while (!is_stopped(c->table))
		usleep(SLEEP_STEP_US);
	return (NULL);
}

void	*coder_routine(void *arg)
{
	t_coder	*c;
	t_table	*t;
	long	end;

	c = (t_coder *)arg;
	t = c->table;
	if (!wait_start(c))
		return (NULL);
	if (c->first == c->second)
		return (solo_routine(c));
	while (!is_stopped(t))
	{
		end = compile_once(c);
		if (end < 0)
			break ;
		log_state(c, "is debugging");
		end += t->args.time_to_debug * 1000L;
		sleep_until(t, end);
		log_state(c, "is refactoring");
		sleep_until(t, end + t->args.time_to_refactor * 1000L);
	}
	return (NULL);
}
