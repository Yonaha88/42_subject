/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   utils.c                                            :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: kyonaha <kyonaha@student.42tokyo.jp>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/10/06 12:22:41 by kyonaha           #+#    #+#             */
/*   Updated: 2026/10/23 16:37:33 by kyonaha          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "codexion.h"

int	is_stopped(t_table *t)
{
	int	stop;

	pthread_mutex_lock(&t->stop_mutex);
	stop = t->stop;
	pthread_mutex_unlock(&t->stop_mutex);
	return (stop);
}

void	set_stop(t_table *t)
{
	pthread_mutex_lock(&t->stop_mutex);
	t->stop = 1;
	pthread_mutex_unlock(&t->stop_mutex);
}

void	wake_all(t_table *t)
{
	int	i;

	pthread_mutex_lock(&t->arbiter);
	i = 0;
	while (i < t->ready_coders)
	{
		pthread_cond_signal(&t->coders[i].wake);
		i++;
	}
	pthread_mutex_unlock(&t->arbiter);
}
