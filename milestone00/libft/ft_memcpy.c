/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_memcpy.c                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: kyonaha <kyonaha@student.42tokyo.jp>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/04/24 10:20:36 by kyonaha           #+#    #+#             */
/*   Updated: 2026/04/28 16:29:43 by kyonaha          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

void	*ft_memcpy(void *dest, const void *src, size_t num)
{
	size_t	idx;

	idx = 0;
	while (idx < num)
	{
		((unsigned char *)dest)[idx] = ((unsigned char *)src)[idx];
		idx++;
	}
	return (dest);
}
