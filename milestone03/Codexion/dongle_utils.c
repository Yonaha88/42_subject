/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   dongle_utils.c                                     :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: kyonaha <kyonaha@student.42tokyo.jp>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/10/06 12:23:35 by kyonaha           #+#    #+#             */
/*   Updated: 2026/10/06 12:23:36 by kyonaha          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "codexion.h"

int	dongle_usable(t_dongle *d, long now)
{
	int	usable;

	pthread_mutex_lock(&d->mutex);
	usable = (d->holder == 0 && now >= d->available_at);
	pthread_mutex_unlock(&d->mutex);
	return (usable);
}

long	dongle_available_at(t_dongle *d)
{
	long	at;

	pthread_mutex_lock(&d->mutex);
	at = d->available_at;
	pthread_mutex_unlock(&d->mutex);
	return (at);
}

void	dongle_take(t_dongle *d, int id)
{
	pthread_mutex_lock(&d->mutex);
	heap_pop(&d->queue);
	d->holder = id;
	pthread_mutex_unlock(&d->mutex);
}

void	dongle_release(t_dongle *d, long available_at)
{
	pthread_mutex_lock(&d->mutex);
	d->holder = 0;
	d->available_at = available_at;
	pthread_mutex_unlock(&d->mutex);
}
