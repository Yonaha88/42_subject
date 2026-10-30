/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   monitor.c                                          :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: kyonaha <kyonaha@student.42tokyo.jp>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/10/06 12:23:00 by kyonaha           #+#    #+#             */
/*   Updated: 2026/10/06 12:23:01 by kyonaha          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "codexion.h"

static int	burned_out(t_coder *c)
{
	long	elapsed;

	pthread_mutex_lock(&c->state_mutex);
	elapsed = now_us() - c->last_compile;
	pthread_mutex_unlock(&c->state_mutex);
	return (elapsed > c->table->args.time_to_burnout * 1000L);
}

static int	all_done(t_table *t)
{
	int	i;
	int	done;

	i = 0;
	while (i < t->args.number_of_coders)
	{
		pthread_mutex_lock(&t->coders[i].state_mutex);
		done = t->coders[i].compiles >= t->args.number_of_compiles_required;
		pthread_mutex_unlock(&t->coders[i].state_mutex);
		if (!done)
			return (0);
		i++;
	}
	return (1);
}

void	stop_simulation(t_table *t)
{
	pthread_mutex_lock(&t->log_mutex);
	set_stop(t);
	pthread_mutex_unlock(&t->log_mutex);
	wake_all(t);
}

static int	check_coders(t_table *t)
{
	int	i;

	i = 0;
	while (i < t->args.number_of_coders)
	{
		if (burned_out(&t->coders[i]) && log_burnout(&t->coders[i]))
		{
			wake_all(t);
			return (1);
		}
		i++;
	}
	if (!all_done(t))
		return (0);
	stop_simulation(t);
	return (1);
}

void	*monitor_routine(void *arg)
{
	t_table	*t;

	t = (t_table *)arg;
	while (!is_stopped(t))
	{
		if (check_coders(t))
			break ;
		usleep(MONITOR_INTERVAL_US);
	}
	return (NULL);
}
