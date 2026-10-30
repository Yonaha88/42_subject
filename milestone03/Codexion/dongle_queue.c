/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   dongle_queue.c                                     :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: kyonaha <kyonaha@student.42tokyo.jp>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/10/06 12:22:52 by kyonaha           #+#    #+#             */
/*   Updated: 2026/10/23 21:16:26 by kyonaha          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "codexion.h"

void	dongle_enqueue(t_dongle *d, t_request req)
{
	pthread_mutex_lock(&d->mutex);
	heap_push(&d->queue, req);
	pthread_mutex_unlock(&d->mutex);
}

int	dongle_is_first(t_dongle *d, int id)
{
	t_request	*top;
	int			first;

	pthread_mutex_lock(&d->mutex);
	top = heap_peek(&d->queue);
	first = (top != NULL && top->coder_id == id);
	pthread_mutex_unlock(&d->mutex);
	return (first);
}
